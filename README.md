# Mock Generator
A tool to generate the basic mocks and asserts for faster unit testing. 

## Introduction
A typical unit test looks like this (AAA pattern):
* Arrange – Setup and prepare the various objects and prerequisites.
* Act – Invoke the tested code by calling the tested function for example.
* Assert – Verify the outcome. This can be the return value of the tested 
function and/or some side effects.

As it turns out, much of the time spent on doing unit tests is wasted on wiring
the various modules and functions and only a fraction of the time is spent on
the actual logic of the test. The `Arrange` and `Assert` sections are notorious
in that regard. 

This tool is meant to save you much of the time and effort of generating 
boilerplates, by generating the `Arrange` and `Assert` sections. 
The generated code can then be used as is, or altered according to your needs.

## Usage
Note: All examples assume the 
[pytest-mock](https://pypi.org/project/pytest-mock/) which is a fixture for
[pytest](https://pypi.org/project/pytest/). 

### Simple example
Let's start with a simple code example. Say you have a module `os_wrapper.py`:
```python
import os 

def os_remove_wrap(filename):
    os.remove(filename)
```
You would like to test that the `os.remove` function is called with the same
value sent to your wrapping function. The test would look something like this:
```python
def test_os_remove_wrap(mocker):
    # Arrange: setup any mocks to avoid deleting actual files
    
    # Act: invoking the tested code
    os_wrapper.os_remove_wrap('/my/path/to/file.txt')
    
    # Assert: verifying that the original os.remove function was called
```

#### Generating the Arrange section
The following code sends the tested module to the tool, along with instructions 
which indicate the desired testing framework and which mocks to generate
(we would like to use pytest-mock fixture and only mock the referenced 
modules):   

```python
import os_wrapper
from mock_autogen.pytest_mocker import PytestMocker

generated_mocks = PytestMocker(os_wrapper).mock_modules().generate() 
```
The `generated_mocks` variable now has the desired code: 
```python
# mocked modules
mock_os = mocker.MagicMock(name='os')
mocker.patch('os_wrapper.os', new=mock_os)
```
Simply copy the code and place it in your test, before the `Act` section: 
```python
import os_wrapper

def test_os_remove_wrap(mocker):
    # Arrange: setup any mocks to avoid deleting actual files
    # auto generated code
    # mocked modules
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('os_wrapper.os', new=mock_os)
    
    # Act: invoking the tested code
    os_wrapper.os_remove_wrap('/my/path/to/file.txt')
    
    # Assert: verifying that the original os.remove function was called
```

#### Generating the Assert section
Now it's time to add the asserts. Add the following code right after the Act 
step:
```python
import mock_autogen

generated_asserts = mock_autogen.generator.generate_asserts(mock_os)
```
The `mock_os` is the mocked object you created earlier.

The `generated_asserts` variable now has the desired code: 
```python
mock_os.remove.assert_called_once_with('/my/path/to/file.txt')
```
Place that code right after the act phase and you're done!

The complete test function:
```python
import os_wrapper

def test_os_remove_wrap(mocker):
    # Arrange: setup any mocks to avoid deleting actual files
    # auto generated code
    # mocked modules
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('os_wrapper.os', new=mock_os)
    
    # Act: invoking the tested code
    os_wrapper.os_remove_wrap('/my/path/to/file.txt')
    
    # Assert: verifying that the original os.remove function was called
    # auto generated code
    mock_os.remove.assert_called_once_with('/my/path/to/file.txt')
```
As can be seen, most of the code was autogenerated so you can focus on the Act.

### Complex example
The previous example was meant to demonstrate how to use the tool. If you have
experience with pytest-mock than you could have probably come up with the same
boilerplate code by yourself in a reasonable time. The next example requires 
the exact same steps to invoke the tool as before, but the benefit is much 
greater.  

Let's assume you have a module `zip_writer.py` which holds a function to
process a string sent to it and then add it to a zip file:
```python
import zipfile

def process_and_zip(zip_path, file_name, contents):
    processed_contents = "processed " + contents  # some complex logic
    with zipfile.ZipFile(zip_path, 'w') as zip_container:
        zip_container.writestr(file_name, processed_contents)
```
Although this is a very short function, which does not do anything complex, 
writing the test code takes a lot of time. It's the fact that the function uses
a context manager makes the testing more complex than it should be. 

Since the process of generating the test code is the same as in the previous 
example, there is no need to repeat it. Let's look at the complete code:
```python
import zip_writer

def test_process_and_zip(mocker):
    # Arrange: auto generated code 
    mock_zipfile = mocker.MagicMock(name='zipfile')
    mocker.patch('tests.sample.code.tested_module.zipfile', new=mock_zipfile)
    
    # Act: invoking the tested code
    zip_writer.process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # Assert: auto generated code
    mock_zipfile.ZipFile.assert_called_once_with('/path/to.zip', 'w')
    mock_zipfile.ZipFile.return_value.__enter__.assert_called_once_with()
    mock_zipfile.ZipFile.return_value.__enter__.return_value.writestr. \
        assert_called_once_with('in_zip.txt', 'processed foo bar')
    mock_zipfile.ZipFile.return_value.__exit__. \
        assert_called_once_with(None, None, None)
```
Look at all the asserts. They are very useful: 
* Checking that we opened the zip file with the right parameters.
* Checking that we wrote the correct data to the proper file.
* And finally, ensuring that `__enter__` and `__exit__` are called, so there 
are no open file handles which could cause problems.

Can you imagine the time it would have taken you to code this on your own?

### What's Next
After you have followed through this example, you can use the Mock Generator 
to **mock everything**. This way you can see all the possibilities of mocks. You 
can also print the result right away, to avoid having to inspect variables. 
It can look something like this:
```python
import os_wrapper
from mock_autogen.pytest_mocker import PytestMocker

print(PytestMocker(os_wrapper).mock_everything().generate()) 
```
What you would get is:
```python
# mocked modules
mock_os = mocker.MagicMock(name='os')
mocker.patch('os_wrapper.os', new=mock_os)
# mocked functions
mock_os_remove_wrap = mocker.MagicMock(name='os_remove_wrap')
mocker.patch('os_wrapper.os_remove', new=mock_os_remove_wrap)
# calls to generate_asserts, put this after the 'act'
import mock_autogen
print(mock_autogen.generator.generate_asserts(mock_os, name='mock_os'))
print(mock_autogen.generator.generate_asserts(mock_os_remove_wrap, name='mock_os_remove_wrap'))
```
Notice the mocked functions section, it allows you to mock functions in
that model. This is useful when you're testing a function which uses
another function you would like to mock.

You even get the calls to generate the asserts prepared for you, place
this code after the act section as shown in the simple example. 

## Wrapping up
I hope that by now you were convinced that this tool can save you a lot of 
time. 

See `tests` folder for additional usage examples like mocking classes and 
instances, using fixtures to share mocks between tests and much more.

If you would like to contribute, I'm accepting pull requests :)
