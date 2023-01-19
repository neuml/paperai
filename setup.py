# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    DESCRIPTION = f.read()

# Optional dependencies
extras = {}

# Development dependencies
extras["dev"] = ["black", "coverage", "coveralls", "httpx", "pre-commit", "pylint"]

setup(
    name="paperai",
    version="2.1.0",
    author="NeuML",
    description="AI-powered literature discovery and review engine for medical/scientific papers",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/neuml/paperai",
    project_urls={
        "Documentation": "https://github.com/neuml/paperai",
        "Issue Tracker": "https://github.com/neuml/paperai/issues",
        "Source Code": "https://github.com/neuml/paperai",
    },
    license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    keywords="search embedding machine-learning nlp covid-19 medical scientific papers",
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "paperai = paperai.shell:main",
        ],
    },
    install_requires=[
        "networkx>=2.4",
        "PyYAML>=5.3",
        "python-dateutil>=2.8.1",
        "regex>=2020.5.14",
        "rich>=12.0.1",
        "text2digits>=0.1.0",
        "txtai[api,similarity]>=4.3.1",
        "txtmarker>=1.0.0",
    ],
    extras_require=extras,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
)
