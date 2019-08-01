import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mock-generator",
    version="0.2.1",
    description="Generate python mocks and assertions quickly",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pksol/mock_autogen",
    author="Peter Kogan",
    author_email="kogan.peter@gmail.com",
    python_requires='>=3.3',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=["mock"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-mock"],
    test_suite="tests")
