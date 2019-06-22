"""Install script for ``pysfn``.

Usage::

    pip install pysfn
"""

import pathlib
import setuptools

parent = pathlib.Path(__file__).parent
long_description = (parent / "README.md").read_text()
version = (parent / "VERSION").read_text().strip()
classifiers = [
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    (
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)")]

setuptools.setup(
    name="pysfn",
    version=version,
    license="GPL3",
    author="Ben North",
    author_email="ben@redfrontdoor.org",
    maintainer="Ben North",
    maintainer_email="ben@redfrontdoor.org",
    description="Compile Python code to AWS Step Function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bennorth/pyawssfn",
    classifiers=classifiers,
    keywords="aws sfn lambda step functions compiler",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires="~=3.6",
    install_requires=["click", "attrs"],
    extras_require={"dev": ["pytest"]},
    project_urls={"Bugs": "https://github.com/bennorth/pyawssfn/issues"})
