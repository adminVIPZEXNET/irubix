from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="irubix",
    version="0.1.0",
    author="Your Name",
    description="کتابخانه ساده و کاربردی برای ساخت ربات روبیکا، مبتنی بر maxrubika",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adminVIPZEXNET/irubix",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["maxrubika>=1.18.1"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
