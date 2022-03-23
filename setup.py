# setup.py
from pyhades import __version__
import setuptools
import platform

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    _requirements = fh.read()

system_platform = platform.system()

setuptools.setup(
    name="PyHades",
    version=__version__,
    author="KnowAI",
    author_email="dev.know.ai@gmail.com",
    description="A python library to develop continuous tasks using sync or async concurrent threads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU AFFERO GENERAL PUBLIC LICENSE",
    url="https://github.com/know-ai/hades",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=_requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU AFFERO GENERAL PUBLIC LICENSE",
        "Operating System :: OS Independent",
    ]
)
