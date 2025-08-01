"""Setup script for Agentical application."""

from setuptools import setup, find_packages
import os

# Read README file
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "Agentical - AI Desktop Automation Application"

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="agentical",
    version="1.0.0",
    author="spawn9859",
    description="Windows-compatible agentic AI application for desktop automation using Google Gemini API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spawn9859/Agentical",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentical=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "config/*.yml"],
    },
    zip_safe=False,
    keywords="automation ai desktop gemini api windows",
    project_urls={
        "Bug Reports": "https://github.com/spawn9859/Agentical/issues",
        "Source": "https://github.com/spawn9859/Agentical",
        "Documentation": "https://github.com/spawn9859/Agentical/wiki",
    },
)