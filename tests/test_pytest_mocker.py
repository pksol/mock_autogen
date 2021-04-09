import re

import tests
import mock_autogen
from mock_autogen.pytest_mocker import PytestMocker


class TestPytestMocker:
    def test__init__(self):
        mocker = PytestMocker(tests.sample.code.tested_module, "my_module")

        assert tests.sample.code.tested_module == mocker.mocked
        assert "my_module" == mocker.name
        assert {
            'mock_modules': False,
            'mock_functions': False,
            'mock_builtin': False,
            'mock_classes': False,
            'mock_referenced_classes': False,
            'mock_classes_static': False,
            'prepare_asserts_calls': False
        } == mocker.kwargs

    def test_mock_modules(self):
        mocker = PytestMocker(tests.sample.code.tested_module).mock_modules()

        assert mocker.kwargs['mock_modules']

    def test_mock_functions(self):
        mocker = PytestMocker(tests.sample.code.tested_module).mock_functions()

        assert mocker.kwargs['mock_functions']

    def test_mock_builtin(self):
        mocker = PytestMocker(tests.sample.code.tested_module).mock_builtin()

        assert mocker.kwargs['mock_builtin']

    def test_mock_classes(self):
        mocker = PytestMocker(tests.sample.code.tested_module).mock_classes()

        assert mocker.kwargs['mock_classes']

    def test_mock_referenced_classes(self):
        mocker = PytestMocker(
            tests.sample.code.tested_module).mock_referenced_classes()

        assert mocker.kwargs['mock_referenced_classes']

    def test_mock_classes_static(self):
        mocker = PytestMocker(
            tests.sample.code.tested_module).mock_classes_static()

        assert mocker.kwargs['mock_classes_static']

    def test_prepare_asserts_calls(self):
        mocker = PytestMocker(
            tests.sample.code.tested_module).prepare_asserts_calls()

        assert mocker.kwargs['prepare_asserts_calls']

    def test_mock_everything(self):
        mocker = PytestMocker(
            tests.sample.code.tested_module).mock_everything()

        assert {
            'mock_modules': True,
            'mock_functions': True,
            'mock_builtin': True,
            'mock_classes': True,
            'mock_referenced_classes': True,
            'mock_classes_static': True,
            'prepare_asserts_calls': True
        } == mocker.kwargs

    def test_use_defaults(self):
        mocker = PytestMocker(tests.sample.code.tested_module).use_defaults()

        assert {} == mocker.kwargs

    def test_generate(self, mocker):
        # mocked modules
        mock_mock_autogen = mocker.MagicMock(name='mock_autogen')
        mocker.patch('mock_autogen.pytest_mocker.mock_autogen',
                     new=mock_mock_autogen)

        # act
        PytestMocker(mock_autogen.pytest_mocker,
                     name='pytest_mocker').mock_modules().generate()

        # assert
        generated = mock_autogen.generate_asserts(mock_mock_autogen)
        assert re.match(
            r"^mock_mock_autogen.generator.generate_mocks."
            r"assert_called_once_with\(framework=<MagicMock "
            r"name='mock_autogen.generator.MockingFramework.PYTEST_MOCK' "
            r"id='\d+'>, mock_builtin=False, mock_classes=False, "
            r"mock_classes_static=False, mock_functions=False, "
            r"mock_modules=True, mock_referenced_classes=False, "
            r"mocked=<module 'mock_autogen.pytest_mocker'.*>, "
            r"name='pytest_mocker', prepare_asserts_calls=False\)$", generated)

    def test_generate_functional(self):
        generated_mocks = PytestMocker(
            mock_autogen.pytest_mocker).mock_modules().generate()

        assert """# mocked modules
mock_mock_autogen = mocker.MagicMock(name='mock_autogen')
mocker.patch('mock_autogen.pytest_mocker.mock_autogen', new=mock_mock_autogen)
""" == generated_mocks
