from setuptools import setup, find_packages
import os

def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Unity Package Forge - Gerador profissional de pacotes Unity"

def get_version():
    try:
        import re
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'\[(\d+\.\d+\.\d+)\]', content)
            if match:
                return match.group(1)
    except:
        pass
    return "1.0.0"

setup(
    name="unity-package-forge",
    version=get_version(),
    author="Nathan da Silva Miranda",
    author_email="natteens@gmail.com",
    description="Gerador profissional de pacotes Unity com integração GitHub",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Natteens/UnityPackageForge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "customtkinter>=5.2.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=5.0",
            "pytest>=6.0",
            "black",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "unity-package-forge=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ui": ["*.ico"],
    },
    keywords=[
        "unity", "unity3d", "package", "generator", "github",
        "gamedev", "unity-package-manager", "upm"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Natteens/UnityPackageForge/issues",
        "Source": "https://github.com/Natteens/UnityPackageForge",
        "Documentation": "https://github.com/Natteens/UnityPackageForge/blob/main/README.md",
    },
)
