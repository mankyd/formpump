#!/usr/bin/env python
#
# Copyright 2011 Dave Mankoff
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.



import setuptools

version = "0.1.2"

setuptools.setup(
    name="formpump",
    version=version,
    packages = setuptools.find_packages(),
    author="Dave Mankoff",
    author_email="mankyd@gmail.com",
    url="http://ohthehugemanatee.net/",
    download_url="",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="FormPump is a tool that integrates with popular templating engines, allowing you the cleanly fill in HTML forms",
)
