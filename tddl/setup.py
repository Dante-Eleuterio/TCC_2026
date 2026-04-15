from setuptools import setup, Extension, find_packages
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


# setup (
#     name="tddl",
#     version="0.1.0",
#     author="Dante Eleuterio, Felipe Bombardelli",
#     author_email="",
#     url="https://github.com/Dante-Eleuterio/TCC_2026",
#     description="",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     packages = ['tddl'],
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#     ],
#     python_requires='>=3.6',

#     entry_points={'console_scripts': [
#         'tddl = tddl:app_main',
#     ]},

#     # configure compilation for c code
#     # cmdclass={'install': CustomInstall},
#     # ext_modules=[module],
#     # include_package_data=True,
# )
setup(
    name="tddl",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tddl=tddl.__main__:main",
        ],
    },
)