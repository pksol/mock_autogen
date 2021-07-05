# Mock Generator
![](https://github.com/pksol/mock_autogen/workflows/CI/badge.svg?branch=master)
![](https://img.shields.io/pypi/v/mock-generator.svg)
![](https://img.shields.io/pypi/pyversions/mock-generator.svg)
![](https://codecov.io/gh/pksol/mock_autogen/branch/master/graph/badge.svg)
![](https://img.shields.io/powershellgallery/p/DNS.1.1.1.1)
![](https://img.shields.io/pypi/l/mock-generator.svg)

A tool to generate the basic mocks and asserts for faster unit testing. 

## Introduction
A typical unit test looks like this (AAA pattern):
* Arrange – Setup and prepare the various objects and prerequisites.
* Act – Invoke the tested code by calling the tested function.
* Assert – Verify the outcome. This can be the return value of the tested 
function and/or some side effects.

When using mocks, much time is wasted on the wiring.
The `Arrange` and `Assert` sections are notorious in that regard.
Only a fraction of the time is spent on the actual logic of the test.

This tool is meant to save you time, 
by generating the `Arrange` and `Assert` sections for you. 
The generated code can then be used as is, or altered according to your needs.

## Usage
Note: All examples assume usage of the 
[pytest-mock](https://pypi.org/project/pytest-mock/) which is a fixture for
[pytest](https://pypi.org/project/pytest/).

### Getting Started
Let's assume you have a module named `tested_module.py` which holds a function
to process a string sent to it and then add it to a zip file:
```python
import zipfile

def process_and_zip(zip_path, file_name, contents):
    processed_contents = "processed " + contents  # some complex logic
    with zipfile.ZipFile(zip_path, 'w') as zip_container:
        zip_container.writestr(file_name, processed_contents)
```
This is the unit under test, or UUT.

Although this is a very short function, 
writing the test code takes a lot of time. It's the fact that the function uses
a context manager makes the testing more complex than it should be.
*If you don't believe me, try to manually write mocks and asserts which verify
that `zip_container.writestr` was called with the right parameters.*

In any case, you start with a test skeleton:

```python
import mock_autogen
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker):
    # Arrange: todo  
    
    # Act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # Assert: todo
```
Now it's time to use Mock Generator instead of manually writing the 'Arrange' 
and 'Assert' sections.

#### Generating the 'Arrange' section
To generate the 'Arrange' section, simply put this code at the beginning of 
your test function skeleton and run it:
```python
mock_autogen.generate_uut_mocks(process_and_zip)
```
This will generate the 'Arrange' section for you:
```python
# mocked dependencies
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
```
The generated code is returned, printed to the console and also copied to the
clipboard for your convenience. 
Just paste it (as simple as ctrl+V) at the start of your test function:
```python
import mock_autogen
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker):
    # mocked dependencies
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
    
    # Act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # Assert: todo
```

Excellent! Arrange section is ready.

#### Generating the Assert section
Now it's time to add the asserts. Add the following code
**at the 'Assert'** step:
```python
mock_autogen.generate_asserts(mock_ZipFile)
```
The `mock_ZipFile` is the mock object you generated earlier.
Now execute the test function to get the assert section: 
```python
assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)
```
Wow, that's a handful of asserts! Some are very useful: 
* Checking that we opened the zip file with the right parameters.
* Checking that we wrote the correct data to the proper file.
* Finally, ensuring that `__enter__` and `__exit__` are called, so there 
are no open file handles which could cause problems.

You can remove any generated line which you find unnecessary.   

Paste that code right after the act phase, and you're done!

The complete test function:
```python
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker):
    # mocked dependencies
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
    
    # Act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    assert 1 == mock_ZipFile.call_count
    mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
    mock_ZipFile.return_value.__enter__.assert_called_once_with()
    mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
    mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)
```
Can you imagine the time it would have taken you to code this on your own?

### What's Next
#### Asserting Existing Mocks
At times, you may be editing a test code already containing mocks, or
you choose to write the mocks yourself, to gain some extra control.

Mock Generator can generate the assert section for standard 
Python mocks, even if they were not created using the Mock Generator. 

Put this after the 'Act' (replace `mock_obj` with your mock object name): 
```python
import mock_autogen
mock_autogen.generate_asserts(mock_obj)
```
Take the generated code and paste it at the 'Assert' section. 

#### Generating the 'Arrange' and 'Assert' sections in one call
You can make the `generate_uut_mocks_with_asserts` call create the 
`generate_asserts` code for you (instead of having to call 
`generate_uut_mocks`):
```python
import mock_autogen
mock_autogen.generate_uut_mocks_with_asserts(function_under_test)
```

#### Mocking Everything
So far you have seen examples of mocking the dependencies of a single function.
Mock Generator can generate mocks for objects, classes and entire modules!

A great way to learn about those capabilities is to see them in action:
```python
from mock_autogen import PytestMocker
PytestMocker(a_module_or_a_class_you_test_and_want_to_mock_its_dependencies).mock_everything().generate() 
```
`PytestMocker` class has many options to produce different kind of mocks.
See its documentation for further details.

## Wrapping up
I hope that you were convinced that this tool can save you a lot of time. 

If you have improvement suggestions, bug reports, 
or would like to contribute pull requests, let me know.
