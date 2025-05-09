from setuptools import setup, find_packages

setup(
    name="unity-package-generator",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'package-generator=package_generator:main',
        ],
    },
    author="Natteens",
    description="Gerador de pacotes para Unity com integração GitHub",
    keywords="unity, package, generator",
    python_requires=">=3.6",
)