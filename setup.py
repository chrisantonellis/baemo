import io
import os
import sys
import shutil
import subprocess
import setuptools


# read module version file
setup_abs_path = os.path.abspath(os.path.dirname(__file__))
version_abs_path = os.path.join(setup_abs_path, "baemo", "__version__.py")
module_metadata = {}
with open(version_abs_path) as file_handle:
    exec(file_handle.read(), module_metadata)


setuptools.setup(
    name="baemo",
    version=module_metadata["__version__"],
    description="MongoDB ORM / ODM",
    keywords="mongodb pymongo orm odm relationship reference unit-of-work",
    url="https://github.com/chrisantonellis/baemo",

    author="Christopher Antonellis",
    author_email="christopher.antonellis@gmail.com",
    license="MIT",
    packages=[
        "baemo"
    ],
    install_requires=[
        "pymongo"
    ],
    extras_require={
        "tests": [
            "green",
            "coverage"
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ]
)
