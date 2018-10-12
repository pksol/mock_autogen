# mock autogen
A tool to auto generate the basic mocks and asserts for faster unit testing. 

## Introduction
A typical unit test looks like this (AAA pattern):
* Arrange – Setup and prepare the various objects and prerequisites.
* Act – Invoke the tested code by calling the tested function for example.
* Assert – Verify the outcome. This can be the return of the tested function 
and/or some side effects.

As it turns out, much of the time spent on doing unit tests is wasted on wiring
the various modules and functions and only a fraction of the time is spend on
the actual logic of the test. The Arrange and Assert sections are notorious in
that regard. 

This tool is meant to save you much of the time and effort of generating 
boilerplates, by generating the Arrange and Assert sections automatically. The 
generated code can then be used as is or altered according to your needs.

## Usage
### Simple example
Let's start with a simple code example. Say you have a module `os_wrapper.py`:
```python
import os 

def os_remove_wrap(filename):
    os.remove(filename)
```
You would like to test that the `os.remove` function is called with the same
value sent to your wrapping function. 

### Generating the Arrange section
The following code sends the tested module to the tool, along with parameters 
which indicate the desired testing framework and which mocks to generate
(we would like to use pytest-mock fixture and only mock the referenced 
modules):   

```python
import os_wrapper
import mock_autogen

generated_mocks = mock_autogen.generator.generate_mocks(
        mock_autogen.generator.MockingFramework.PYTEST_MOCK,
        os_wrapper, mock_modules=True, mock_functions=False, 
        mock_builtin=False, mock_classes=False, 
        mock_referenced_classes=False, mock_classes_static=False)
```
The `generated_mocks` variable now has the desired code: 
```python
mock_os = mocker.MagicMock(name='os')
mocker.patch('os_wrapper.os', new=mock_os)
```
Simply copy the code and place it in your test. 

### Generating the Assert section
After the previous step, your test function can look like this:
```python
import os_wrapper
import mock_autogen

# your test function
def test_os_remove_wrap(mocker):
    # auto generated code from previous section
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('os_wrapper.os', new=mock_os)
    
    # your code Act: invoking the tested code
    os_wrapper.os_remove_wrap('/my/path/file.txt')
```
Now it's time to add the asserts. Add the following code right after the Act 
step:
```python
generated_call_list = mock_autogen.generator.generate_call_list(mock_os, 
    mock_name='mock_os')
```
The `generated_call_list` variable now has the desired code: 
```python
mock_os.remove.assert_called_once_with('/my/path/file.txt')
```
Place that code right after the act phase and you're done!

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
a context manager makes the testing more complex than it should be. The process 
of generating the test code is the same as in the previous example, so let's 
look at the final code:
```python
import zip_writer

# your test function
def test_process_and_zip(mocker):
    # auto generated code 
    mock_zipfile = mocker.MagicMock(name='zipfile')
    mocker.patch('tests.sample.code.tested_module.zipfile', new=mock_zipfile)
    
    # your code Act: invoking the tested code
    zip_writer.process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # auto generated code
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

Can you imagine the time it would have taken you to implement this on your own?

I hope that by now you were convinced that this tool can save you a lot of 
time. See `tests` for additional usage examples like mocking classes and 
instances, using fixtures to share mocks between tests and more.

