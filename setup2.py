#!/usr/bin/env python
## Copyright (C) 2003-2010  Jeffrey O'Neill
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import sys
import os
import glob
import shutil
import pkgutil
from distutils.core import setup

from openstv.version import v as OpenSTV_version

__revision__ = "$Id: setup.py 777 2010-06-06 13:04:54Z jeff.oneill $"

# Remove the build and dist folders
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

# generic arguments for setup()
name = "OpenSTV"
description = "Implements the single transferable vote, instant runoff "\
              "voting, and several other voting systems."
author = "Jeff O'Neill"
author_email = "jeff.oneill@openstv.org"
url = "http://www.openstv.org"
license = "Gnu General Public License version 2"

packages = ["openstv",
            "openstv.MethodPlugins", 
            "openstv.LoaderPlugins",
            "openstv.ReportPlugins"]

data_files = [ ("", ["openstv/Help.html",
                     "openstv/License.html"]),
               ("Icons",
                 ["openstv/Icons/pie.ico",
                  "openstv/Icons/blt.ico",
                  "openstv/Icons/splash.png"]) ]

# Get list of plugins because they won't be automatically included
includes = []
pluginPackageNames = ["openstv.MethodPlugins", "openstv.LoaderPlugins", 
                      "openstv.ReportPlugins"]
for x in pluginPackageNames:
    package = __import__(x, fromlist="dummy")
    ppath = package.__path__
    pname = package.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(ppath, pname):
        includes.append(modname)

# For *nix, data_files goes into the /usr directory, which 
# we don't want.
# pacakge_data doesn't appear to work for sdist so use MANIFEST.in

# Create MANIFEST.in
f = open("MANIFEST.in", "w")
print >> f, r"""
include CHANGELOG.txt
include README.txt
include openstv/Help.html
include openstv/License.html
include openstv/Icons/splash.png
include openstv/Icons/blt.ico
include openstv/Icons/pie.ico
include openstv/Icons/blt.icns
include openstv/Icons/pie.icns
"""
f.close()

setup(name = name,
      version = OpenSTV_version,
      description = description,
      author = author,
      author_email = author_email,
      url = url,
      license = license,
      packages = packages,
      )
