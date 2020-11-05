#!/usr/bin/env python3

import os
from io import open

from setuptools import find_packages, setup


about, project_path = {}, os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(project_path, "py_querybuilder", "__version__.py"), "r") as f:
    exec(f.read(), about)  # noqa S102

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    keywords="python querybuilder sql",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "jinjasql",
        "sqlparse",
    ],
    tests_require=[
        "pytest",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    license=about["__license__"],
)
