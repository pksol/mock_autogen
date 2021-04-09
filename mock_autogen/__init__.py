from functools import partial

from mock_autogen.generator import generate_asserts, generate_mocks, \
    MockingFramework

from mock_autogen.pytest_mocker import PytestMocker

# see mock_autogen.generator.generate_mocks for extra parameters and options
generate_uut_mocks = partial(generate_mocks,
                             MockingFramework.PYTEST_MOCK,
                             prepare_asserts_calls=False)

generate_uut_mocks_with_asserts = partial(generate_mocks,
                                          MockingFramework.PYTEST_MOCK,
                                          prepare_asserts_calls=True)
