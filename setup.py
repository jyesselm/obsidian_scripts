#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


with open("README.md", "r", encoding="UTF-8") as f:
    readme = f.read()

with open("requirements.txt", "r", encoding="UTF-8") as f:
    requirements = f.read().splitlines()

setup(
    name="obsidian_scripts",
    version="0.1.0",
    description="A set of scripts for formatting notes for obsidian note program ",
    long_description=readme,
    long_description_content_type="test/markdown",
    author="Joe Yesselman",
    author_email="jyesselm@unl.edu",
    url="https://github.com/jyesselm/obsidian_scripts",
    packages=[
        "obsidian_scripts",
    ],
    package_dir={"obsidian_scripts": "obsidian_scripts"},
    py_modules=["obsidian_scripts/cli"],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="obsidian_scripts",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points={"console_scripts": ["obsidian-scripts = obsidian_scripts.cli:cli"]},
)
