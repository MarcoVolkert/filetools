import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="filetools",
    version="0.0.1",
    author="Marco Volkert",
    author_email="marco.volkert24@gmx.de",
    description="collection of file tooling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarcoVolkert/filetools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)