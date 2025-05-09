from setuptools import setup, find_packages

setup(
    name="unity-package-forge",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'package-generator=src.main:main',
        ],
    },
    author="Natteens",
    description="Gerador de pacotes para Unity com integração GitHub",
    keywords="unity, package, forge",
    python_requires=">=3.6",
)