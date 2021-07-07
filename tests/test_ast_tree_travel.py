import sys
from unittest.mock import sentinel

from mock_autogen.ast_tree_travel import safe_travels, DependencyLister
from tests.sample.code.assignments import split_list, multiple_assignments, \
    annotated_assignments
from tests.sample.code.comprehensions_and_loops import get_square_root_loop, \
    summarize_environ_values_loop, trimmed_strings_loop, \
    get_square_root_loop_external_variable
from tests.sample.code.lambdas import simple_func_using_lambdas
from tests.sample.code.with_statements import simple_anonymous_context, \
    simple_context, outside_lock_context, inside_lock_context, \
    multiple_contexts_same_method, multiple_contexts_different_methods


@safe_travels("a dummy method that might fail")
def node_visit_func(self, node):
    node.made_up_function()


@safe_travels("a dummy method that might fail, but won't proceed afterwards",
              call_generic_visit=False)
def node_visit_func_stop_there(self, node):
    node.made_up_function()


def test_safe_travels_on_func_success(mocker):
    self = mocker.MagicMock(name='self')
    node = mocker.MagicMock(name='node')

    node_visit_func(self, node)

    node.made_up_function.assert_called_once_with()
    self.generic_visit.assert_called_once_with(node)


def test_safe_travels_on_func_failure(mocker):
    # arrange
    mock_dump = mocker.MagicMock(name='dump')
    mock_dump.return_value = "code_dump"
    mocker.patch('mock_autogen.ast_tree_travel.ast.dump', new=mock_dump)
    mock_get_source_segment = mocker.MagicMock(name='get_source_segment')
    mock_get_source_segment.return_value = "code_actual"
    if sys.version_info >= (3, 8):
        mocker.patch('mock_autogen.ast_tree_travel.ast.get_source_segment',
                     new=mock_get_source_segment)
    mock_warning = mocker.MagicMock(name='warning')
    mocker.patch('mock_autogen.ast_tree_travel.logger.warning',
                 new=mock_warning)
    self = mocker.MagicMock(name='self')
    self.warnings = []
    self.source_code = "my = python.code"

    # act
    node_visit_func(self, sentinel.node)

    # assert
    self.generic_visit.assert_called_once_with(sentinel.node)

    mock_dump.assert_called_once_with(sentinel.node)

    if sys.version_info >= (3, 8):
        mock_get_source_segment.assert_called_once_with(
            'my = python.code', sentinel.node)
        warning = '# could not a dummy method that might fail on node:\n' \
                  '#  code_actual\n' \
                  "#  '_SentinelObject' object has no attribute " \
                  "'made_up_function'"
    else:
        mock_get_source_segment.assert_not_called()
        warning = '# could not a dummy method that might fail on node:\n' \
                  '#  code_dump\n' \
                  "#  '_SentinelObject' object has no attribute " \
                  "'made_up_function'"
    mock_warning.assert_called_once_with(warning, exc_info=True)
    assert warning in self.warnings


def test_safe_travels_stop_there_on_func_success(mocker):
    self = mocker.MagicMock(name='self')
    node = mocker.MagicMock(name='node')

    node_visit_func_stop_there(self, node)

    node.made_up_function.assert_called_once_with()
    self.generic_visit.assert_not_called()


def test_safe_travels_stop_there_on_func_failure(mocker):
    # arrange
    mock_dump = mocker.MagicMock(name='dump')
    mock_dump.return_value = "code_dump"
    mocker.patch('mock_autogen.ast_tree_travel.ast.dump', new=mock_dump)
    mock_get_source_segment = mocker.MagicMock(name='get_source_segment')
    mock_get_source_segment.return_value = "code_actual"
    if sys.version_info >= (3, 8):
        mocker.patch('mock_autogen.ast_tree_travel.ast.get_source_segment',
                     new=mock_get_source_segment)
    mock_warning = mocker.MagicMock(name='warning')
    mocker.patch('mock_autogen.ast_tree_travel.logger.warning',
                 new=mock_warning)
    self = mocker.MagicMock(name='self')
    self.warnings = []
    self.source_code = "my = python.code"

    # act
    node_visit_func_stop_there(self, sentinel.node)

    # assert
    self.generic_visit.assert_not_called()

    mock_dump.assert_called_once_with(sentinel.node)

    if sys.version_info >= (3, 8):
        mock_get_source_segment.assert_called_once_with(
            'my = python.code', sentinel.node)
        warning = "# could not a dummy method that might fail, " \
                  "but won't proceed afterwards on node:\n" \
                  '#  code_actual\n' \
                  "#  '_SentinelObject' object has no attribute " \
                  "'made_up_function'"
    else:
        mock_get_source_segment.assert_not_called()
        warning = "# could not a dummy method that might fail, " \
                  "but won't proceed afterwards on node:\n" \
                  '#  code_dump\n' \
                  "#  '_SentinelObject' object has no attribute " \
                  "'made_up_function'"
    mock_warning.assert_called_once_with(warning, exc_info=True)
    assert warning in self.warnings


class TestDependencyLister:
    def test_execute_for_loop_single_variable(self):
        expected_mocked_functions = [
            ('tests.sample.code.comprehensions_and_loops.math', 'sqrt')
        ]

        deps_lister = DependencyLister(get_square_root_loop).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_for_loop_single_variable_ignore_func_calls(self):
        expected_mocked_functions = [
            ('tests.sample.code.comprehensions_and_loops', 'len')
        ]

        deps_lister = DependencyLister(trimmed_strings_loop).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_for_loop_single_variable_with_external_obj_iteration(
            self):
        expected_mocked_functions = [
            ('tests.sample.code.comprehensions_and_loops', 'external_items'),
            ('tests.sample.code.comprehensions_and_loops.math', 'sqrt')
        ]

        deps_lister = DependencyLister(
            get_square_root_loop_external_variable).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_for_loop_multi_variable(self):
        expected_mocked_functions = [
            ('tests.sample.code.comprehensions_and_loops.os.environ', 'items'),
            ('tests.sample.code.comprehensions_and_loops', 'len')
        ]

        deps_lister = DependencyLister(summarize_environ_values_loop).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_lambda_ignore_variable_func_calls(self):
        expected_mocked_functions = [('tests.sample.code.lambdas', 'any'),
                                     ('tests.sample.code.lambdas', 'filter'),
                                     ('tests.sample.code.lambdas', 'len')]

        deps_lister = DependencyLister(simple_func_using_lambdas).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_ignore_multiple_assign_calls(self):
        expected_mocked_functions = [
            ('tests.sample.code.assignments.random', 'randint'),
            ('tests.sample.code.assignments', 'split_list'),
            ('tests.sample.code.assignments', 'len')
        ]

        deps_lister = DependencyLister(multiple_assignments).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_ignore_starred_assign_calls(self):
        expected_mocked_functions = [('tests.sample.code.assignments', 'print')
                                     ]

        deps_lister = DependencyLister(split_list).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_ignore_annotated_assign_calls(self):
        expected_mocked_functions = [
            ('tests.sample.code.assignments.random', 'randint'),
            ('tests.sample.code.assignments', 'split_list'),
            ('tests.sample.code.assignments', 'len'),
            ('tests.sample.code.assignments', 'str')
        ]

        deps_lister = DependencyLister(annotated_assignments).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_anonymous(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements', 'open'),
            ('tests.sample.code.with_statements', 'print')
        ]

        deps_lister = DependencyLister(simple_anonymous_context).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_named(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements', 'open'),
            ('tests.sample.code.with_statements', 'print')
        ]

        deps_lister = DependencyLister(simple_context).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_outside(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements', 'lock'),
            ('tests.sample.code.with_statements', 'single_thread_dict')
        ]

        deps_lister = DependencyLister(outside_lock_context).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_inside(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements.threading', 'Lock'),
            ('tests.sample.code.with_statements', 'single_thread_dict')
        ]

        deps_lister = DependencyLister(inside_lock_context).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_multiple_contexts_same_method(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements', 'lock'),
            ('tests.sample.code.with_statements', 'open')
        ]

        deps_lister = DependencyLister(multiple_contexts_same_method).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)

    def test_execute_with_multiple_contexts_different_methods(self):
        expected_mocked_functions = [
            ('tests.sample.code.with_statements', 'lock'),
            ('tests.sample.code.with_statements.pathlib', 'Path'),
            ('tests.sample.code.with_statements', 'open')
        ]

        deps_lister = DependencyLister(
            multiple_contexts_different_methods).execute()
        assert not deps_lister.warnings
        assert expected_mocked_functions == list(
            deps_lister.dependencies_found)
