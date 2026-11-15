from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="irubix",
    version="0.9.12",
    author="mahdishami",
    description="Async Python bot clients for Rubika, Bale, Soroush Plus and Telegram",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/adminVIPZEXNET/irubix",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
