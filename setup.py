from setuptools import setup, find_packages

setup(
    name="dna-sec",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "biopython>=1.80",
        "yara-python>=4.3.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "dna-sec=dna_sec.cli:scan",
        ],
    },
    package_data={
        "dna_sec": ["rules/*.yar"],
    },
)