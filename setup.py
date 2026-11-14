from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="irubix",
    version="0.7.0",
    author="mahdishami",
    description="Python clients for Rubika, Bale, Soroush Plus bots and Shad user accounts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adminVIPZEXNET/irubix",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["maxrubika>=1.18.1"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
