import ast
import functools
import inspect
import logging
import sys
import textwrap
from collections import OrderedDict
from typing import Callable

logger = logging.getLogger(__name__)


def safe_travels(action: str):
    """
    Takes care of calling `self.generic_visit(node)` and allows the inner
    method to focus on the logic. Including in the case of exception.

    If an exception does happen, a warning in the form of
    `f"# could not {action} on node: {str(node)}"` would be added to
    self.warnings, and the tree travel would continue to the next node.

    Args:
        action: the name of the action

    Returns:
        callable: the decorated method
    """
    def inner_decorator(method):
        @functools.wraps(method)
        def safe_visit(self, node, *args, **kwargs):
            try:
                method(self, node, *args, **kwargs)
            except Exception as e:
                node_repr = ast.dump(node)
                if sys.version_info >= (3, 8) and self.source_code:
                    node_repr = ast.get_source_segment(self.source_code, node)
                node_repr = "\n#  ".join(node_repr.split("\n"))
                warning = f"# could not {action} on node:\n" \
                          f"#  {node_repr}"
                logger.warning(warning, exc_info=True)
                self.warnings.append(warning)
            self.generic_visit(node)

        return safe_visit

    return inner_decorator


class DependencyLister(ast.NodeVisitor):
    """
    Goes over the ast tree of the mocked method or function, finds any
    called functions and objects which are external dependencies.

    Use `execute` to go over the tree and parse it, then use
    `dependencies_found` attribute to get a list of the findings.

    Every item in `dependencies_found` is a tuple with one or two items:
        * For objects: (path to object,)
        * For functions: (path to function, function name).
        Like: ('tests.sample.code.tested_module.random', 'randint')

    Any warnings during the ast parsing would be stored in the `warnings`
    attribute. This list contains every warning as a string item.

    Args:
        mocked: a callable method or function
    """
    def __init__(self, mocked: Callable):
        self.mocked = mocked
        self.outer_module_name = inspect.getmodule(mocked).__name__
        self.source_code = textwrap.dedent(inspect.getsource(mocked))
        self.tree = ast.parse(self.source_code)

        self.dependencies_found = []  # the external func/obj to be mocked
        self.warnings = []  # alert on all the unsupported syntax

        # these are the potential calls, some of them won't be mocked
        # every object is a list of one item: path to object
        # every func is a list of two items: path to function, function name
        self.potential_dependencies = []

        # keys are names while values are true import paths
        # this is used to allow mocking dependencies that were renamed,
        # an example to such rename is an internal import in the UUT function
        self.import_mappings = {}

        # ignore all variable function calls:
        #   if they are parameters or assignments it's hard to know their type,
        #       so it's hard to mock the right thing
        #   if they were created by the result of calling a function that would
        #       be mocked - the user can change or assert for the return_value
        #       of that original mock
        self.ignored_variables = set()

    def execute(self):
        """
        Goes through the source code and collects any dependencies to mock.
        """
        super().visit(self.tree)
        self.dependencies_found = self._prepare_dependencies()
        return self

    def _prepare_dependencies(self):
        """
        These are the functions and objects which will be mocked.

        Returns:
        list of tuple:
            every item is a tuple with two items:
                * For objects: path to object, object name.
                Like: ('tests.sample.code.tested_module', 'static_var')
                * For functions: path to function, function name.
                Like: ('tests.sample.code.tested_module.random', 'randint')
        """
        dependencies = OrderedDict()  # no need to mock same object twice
        for id_and_obj_path in self.potential_dependencies:
            skip = id_and_obj_path[0] in self.ignored_variables
            id_and_obj_path[0] = self.import_mappings.get(
                id_and_obj_path[0],
                self.outer_module_name + '.' + id_and_obj_path[0])
            replaced_path = ".".join(id_and_obj_path)
            *obj_path, obj_name = replaced_path.rsplit('.', 1)
            obj_path = obj_path[0] if obj_path else None
            obj_qualified_name = (
                obj_path,
                obj_name,
            )

            if not skip and obj_qualified_name not in dependencies:
                dependencies[obj_qualified_name] = replaced_path

        return DependencyLister._filter_root_mocks(dependencies)

    @safe_travels("convert a name call into a mock")
    def visit_Name(self, node):
        self.potential_dependencies.append([_stringify_node_path(node)])

    @safe_travels("convert a function call into a mock")
    def visit_Call(self, node):
        id_and_func_path = _stringify_node_path(node.func).split('.', 1)
        self.potential_dependencies.append(id_and_func_path)

    @safe_travels("add internal import to known mappings")
    def visit_Import(self, node):
        for name in node.names:
            self.import_mappings[name.asname if name.asname else name.
                                 name] = name.name

    @safe_travels("add internal import from to known mappings")
    def visit_ImportFrom(self, node):
        for name in node.names:
            self.import_mappings[name.asname if name.asname else name.
                                 name] = node.module + "." + name.name

    @safe_travels("ignore variable assign")
    def visit_Assign(self, node):
        for target in node.targets:
            if not isinstance(target, ast.Subscript):
                target_assign = _stringify_node_path(target)
                self.ignored_variables.add(target_assign)

    @safe_travels("ignore variable annotated assign")
    def visit_AnnAssign(self, node):
        self.ignored_variables.add(node.target.id)

    @safe_travels("ignore with variables")
    def visit_withitem(self, node):
        if node.optional_vars:
            self.ignored_variables.add(node.optional_vars.id)

    @safe_travels("ignore for loop variables")
    def visit_For(self, node):
        self._add_target_variables_to_ignored(node)

    @safe_travels("ignore comprehension variables")
    def visit_comprehension(self, node):
        self._add_target_variables_to_ignored(node)

    @safe_travels("ignore function arguments")
    def visit_FunctionDef(self, node):
        for i, arg in enumerate(node.args.args + node.args.kwonlyargs +
                                [node.args.vararg, node.args.kwarg]):
            if arg:
                # support 'self', 'cls' by pointing it to the Class
                if 0 == i and inspect.ismethod(self.mocked):
                    self_var_name = arg.arg
                    class_name = self.mocked.__qualname__.split('.', 1)[0]
                    self.import_mappings[self_var_name] = \
                        self.outer_module_name + '.' + class_name
                else:
                    self.ignored_variables.add(arg.arg)

    def _add_target_variables_to_ignored(self, node):
        inner_variables = node.target
        if not isinstance(inner_variables, ast.Tuple) and not isinstance(
                inner_variables, ast.List) and not isinstance(
                    inner_variables, ast.Set):
            inner_variables = ast.Tuple(elts=[node.target])
        for inner_variable in inner_variables.elts:
            target_assign = _stringify_node_path(inner_variable)
            self.ignored_variables.add(target_assign)

    @staticmethod
    def _filter_root_mocks(dependencies):
        """
        Avoid mocking the root of called deps, filter them from the list.

        Args:
            dependencies (list of tuple): the original dependencies,
                without filtering

        Returns:
        list of tuple:
            every item is a tuple with two items:
                * For objects: path to object, object name.
                Like: ('tests.sample.code.tested_module', 'static_var')
                * For functions: path to function, function name.
                Like: ('tests.sample.code.tested_module.random', 'randint')
        """
        filtered_deps = OrderedDict()
        replaced_paths = dependencies.values()
        for k, v in dependencies.items():
            if not any(
                    filter(lambda path: path.startswith(v) and path != v,
                           replaced_paths)):
                filtered_deps[k] = v
        return filtered_deps.keys()


def _can_stringify_node_path(node) -> bool:
    """
    Returns:
        whether this node can be stringified.
    """
    return isinstance(node, ast.Name) or isinstance(node, ast.Attribute)


def _stringify_node_path(node):
    """
    Returns the qualified path the node is pointing to.

    Can return something like: var_name.attr.inner_attr.

    Args:
        node (ast.Name or ast.Attribute):

    Returns:
        str: the qualified path the node is pointing to.
    """
    if isinstance(node, ast.Name):
        stringify = node.id
    elif isinstance(node, ast.Attribute):
        stringify = _stringify_node_path(node.value) + "." + node.attr
    else:
        raise TypeError(f"Can't stringify node of type {type(node)}")
    return stringify
