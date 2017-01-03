from distutils.core import setup

setup(
  name="pymongo_basemodel",
  packages=["pymongo_basemodel"],
  license="MIT License",
  version="0.0.1",
  description="pymongo_basemodel is a PyMongo ORM that implements the unit of work pattern",
  author="Christopher Antonellis",
  author_email="christopher.antonellis@gmail.com",
  url="https://github.com/chrisantonellis/pymongo_basemodel",
  download_url="https://github.com/chrisantonellis/pymongo_basemodel/tarball/master",
  keywords=["PyMongo", "MongoDB", "ORM"],
  classifiers=[
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.5",
    "Topic :: Database",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
)