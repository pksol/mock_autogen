import mock_autogen.generator
import tests.sample.code.tested_module


def test_generate_mocks():
    x = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFrameworks.PYTEST_MOCK,
        tests.sample.code.tested_module)
    print x
