#!/usr/bin/env python3
"""
Setup script for metad_fill package.

This allows installation via:
    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metad-fill",
    version="1.0.0",
    author="Joel Debeljak",
    description="Standalone metadata filling and enrichment tool for audio files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sokkohai/plMetaTemp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Topic :: Multimedia :: Sound/Audio",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "metadata-fill=src.metadata_fill:main",
        ],
    },
    include_package_data=True,
    keywords="metadata audio music enrichment database musicbrainz",
)
