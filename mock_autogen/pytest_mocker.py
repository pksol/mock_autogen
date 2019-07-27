import mock_autogen.generator


class PytestMocker:
    """
    A class to wrap the mocker usage for the Pytest Mocker usage.

    Call `mock_.*` methods to set the mocking you would like and then call
    `generate` to get the generated code. If you are unsure what you would like
    to mock, just call `mock_everything`.

    Example: `PytestMock(my_module).mock_modules().mock_functions().generate()`
    would mock the imported modules of `my_module` and its functions / methods.

    Args:
        mocked (object): the object to mock, might be
            `types.ModuleType`, a class or just a plain object instance
        name (str): the name of the mocked object, to be put in the
            generated code. If the name is not provided, the following logic
            would be used to determine its name: for modules - the name of the
            module. For anything else, would be guessed to match the argument
            name sent to the method and finally defaulted to 'arg'
    """

    def __init__(self, mocked, name=''):
        self.mocked = mocked
        self.name = name
        self.kwargs = {
            'mock_modules': False,
            'mock_functions': False,
            'mock_builtin': False,
            'mock_classes': False,
            'mock_referenced_classes': False,
            'mock_classes_static': False
        }

    def mock_modules(self):
        """
        Mock dependant modules which are referenced from the mocked object.

        Relevant only if `mocked` is `types.ModuleType`.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_modules'] = True
        return self

    def mock_functions(self):
        """
        Mock functions / methods defined in the mocked object.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_functions'] = True
        return self

    def mock_builtin(self):
        """
        Mock builtin functions defined in the module.

        Relevant only if `mocked` is `types.ModuleType`.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_builtin'] = True
        return self

    def mock_classes(self):
        """
        Mock classes defined in the module.

        Relevant only if `mocked` is `types.ModuleType`.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_classes'] = True
        return self

    def mock_referenced_classes(self):
        """
        Mock classes referenced in the module but defined elsewhere.

        Relevant only if `mocked` is `types.ModuleType`.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_referenced_classes'] = True
        return self

    def mock_classes_static(self):
        """
        Mock the static functions of the mocked classes. This is important if
        the tested code uses isinstance of accessed class functions directly.

        Relevant only if `mocked` is `types.ModuleType`. Used only if
        mock_classes or mock_referenced_classes is `True`

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs['mock_classes_static'] = True
        return self

    def mock_everything(self):
        """
        Uses the default settings set in mock_autogen.generator.generate_mocks.

        Use this if you are ok with them and would like to save some code and
        be less explicit.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs = {
            'mock_modules': True,
            'mock_functions': True,
            'mock_builtin': True,
            'mock_classes': True,
            'mock_referenced_classes': True,
            'mock_classes_static': True
        }
        return self

    def use_defaults(self):
        """
        Uses the default settings set in mock_autogen.generator.generate_mocks.

        Use this if you are ok with them and would like to save some code and
        be less explicit.

        Returns:
            PytestMocker: the self object for method chaining
        """
        self.kwargs = {}
        return self

    def generate(self):
        """
        Generates the list of mocks in order to mock the dependant modules and
        the functions of a given module, class or object instance.

        Returns:
            str: the initial code to put in your test to mock the desired
                behaviour
        """
        return mock_autogen.generator.generate_mocks(
            framework=mock_autogen.generator.MockingFramework.PYTEST_MOCK,
            mocked=self.mocked,
            name=self.name,
            **self.kwargs)