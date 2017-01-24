#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from fangs import __author__, __contact__, \
    __homepage__, __version__


with open("README.rst") as src:
    readme = src.read()

with open("CHANGELOG.rst") as src:
    changelog = src.read().replace(".. :changelog:", "").strip()

with open("requirements-dev.txt") as src:
    test_requirements = [line.strip() for line in src]


setup(
    name="Fangs",
    version=__version__,
    description="Opinionated utilities for Snakemake pipelines.",
    long_description=readme + "\n\n" + changelog,
    author=__author__,
    author_email=__contact__,
    url=__homepage__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords="snakemake utilities ngs pipeline",
    tests_require=test_requirements,
    py_modules=["fangs"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ],
)
