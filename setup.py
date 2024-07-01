import pathlib
import setuptools

setuptools.setup(
    name="rr_inject",
    version="0.2.0",
    packages=setuptools.find_packages(),
    license='MIT',
    description="Dependency Injection library for Python using decorators.",
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/fredriques/rr-pyinject",
    author="Fredrique Samuels",
    project_urls={
        "Documentation": "https://github.com/fredriques/rr-pyinject?tab=readme-ov-file#readme",
        "Source": "https://github.com/fredriques/rr-pyinject",
        "Health": "https://github.com/fredriques/rr-pyinject/actions",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities"
    ],
    python_requires=">=3.8,<3.12",
    install_requires=[],
    extras_require={},
    include_package_data=True
)
