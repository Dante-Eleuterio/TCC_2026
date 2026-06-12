from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tddl",
    version="1.0.0",
    author="Dante Eleuterio, Felipe Bombardelli",
    author_email="danteeleuterio00@email.com",
    description="Python Framework to help run Unity tests on C code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dante-Eleuterio/TCC_2026",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "tddl=tddl.__main__:main",
        ],
    },
)
