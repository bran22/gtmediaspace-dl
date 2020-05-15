import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gtmediaspace-dl",
    version="0.0.1",
    author="bran22",
    author_email="8986312+bran22@users.noreply.github.com",
    description="Simple tool to download lecture videos from mediaspace.gatech.edu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bran22/gtmediaspace-dl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points=dict(
        console_scripts=[
            'gtmediaspace-dl = gtmediaspace_dl.gtmediaspace_dl:main'
        ]
    ),
    python_requires='>=3.6',
)