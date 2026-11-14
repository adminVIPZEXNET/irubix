from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="irubix",
    version="0.2.0",
    author="",
    description="Independent Python library for Rubika bots with zero third-party dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adminVIPZEXNET/irubix",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
