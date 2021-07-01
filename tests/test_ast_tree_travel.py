import sys
from unittest.mock import sentinel

import mock_autogen.ast_tree_travel


@mock_autogen.ast_tree_travel.safe_travels("a dummy method that might fail")
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
