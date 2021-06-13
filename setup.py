import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()
TESTS_REQUIRE = (HERE / "test-requirements.txt").read_text().splitlines()[1:]

# This call to setup() does all the work
setup(name="mock-generator",
      version="2.1.0",
      description="Generate python mocks and assertions quickly",
      long_description=README,
      long_description_content_type="text/markdown",
      url="https://github.com/pksol/mock_autogen",
      author="Peter Kogan",
      author_email="kogan.peter@gmail.com",
      python_requires='>=3.6',
      license="MIT",
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Operating System :: OS Independent",
      ],
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      setup_requires=["wheel", "pytest-runner"],
      tests_require=TESTS_REQUIRE,
      test_suite="tests")
