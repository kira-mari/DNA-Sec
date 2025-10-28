"""
Pytest configuration and shared fixtures for DNA-Sec tests
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_fasta_content():
    """Sample FASTA content for testing"""
    return """>test_sequence
ATCGATCGATCGATCG
"""


@pytest.fixture
def sample_fasta_file(temp_dir, sample_fasta_content):
    """Create a temporary FASTA file"""
    fasta_file = temp_dir / "test.fasta"
    fasta_file.write_text(sample_fasta_content)
    return str(fasta_file)


@pytest.fixture
def malicious_fasta_content():
    """Sample malicious FASTA content (shellcode-like)"""
    # Encodes shellcode pattern: 31 C0 (xor eax, eax)
    # 31 = 00 11 00 01 = ATCA
    # C0 = 11 00 00 00 = TAAA
    return """>shellcode_test
ATCATAAA
"""


@pytest.fixture
def malicious_fasta_file(temp_dir, malicious_fasta_content):
    """Create a temporary malicious FASTA file"""
    fasta_file = temp_dir / "malicious.fasta"
    fasta_file.write_text(malicious_fasta_content)
    return str(fasta_file)


@pytest.fixture
def clean_dna_sequence():
    """Clean DNA sequence without malicious patterns"""
    return "ATGATGATGGGCGGCGCCGCCTATATATATATAA"


@pytest.fixture
def shellcode_dna_sequence():
    """DNA sequence encoding shellcode (31C0 pattern)"""
    return "ATCATAAA" * 10  # Répète le pattern
