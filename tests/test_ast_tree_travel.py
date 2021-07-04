import sys
from unittest.mock import sentinel

from mock_autogen.ast_tree_travel import safe_travels, DependencyLister
from tests.sample.code.comprehensions_and_loops import get_square_root_loop, \
    summarize_environ_values_loop, trimmed_strings_loop, \
    get_square_root_loop_external_variable


@safe_travels("a dummy method that might fail")
def node_visit_func(self, node):
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
                  '#  code_actual'
    else:
        mock_get_source_segment.assert_not_called()
        warning = '# could not a dummy method that might fail on node:\n' \
                  '#  code_dump'
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
