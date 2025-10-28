"""
Tests unitaires pour le module parser
"""

import pytest
from dna_sec.parser import load_dna_sequence


def test_load_fasta_valid():
    """Test chargement FASTA valide"""
    # Créer un fichier FASTA temporaire
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(">test_sequence\n")
        f.write("ATCGATCGATCG\n")
        temp_path = f.name

    try:
        sequence = load_dna_sequence(temp_path)
        assert sequence == "ATCGATCGATCG"
    finally:
        import os

        os.unlink(temp_path)


def test_load_fasta_invalid_bases():
    """Test rejet de bases invalides"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(">test_sequence\n")
        f.write("ATCGXYZ\n")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="Bases invalides"):
            load_dna_sequence(temp_path)
    finally:
        import os

        os.unlink(temp_path)


def test_load_empty_file():
    """Test fichier vide"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        temp_path = f.name

    try:
        with pytest.raises(ValueError):
            load_dna_sequence(temp_path)
    finally:
        import os

        os.unlink(temp_path)


def test_load_multiline_fasta():
    """Test FASTA multi-lignes"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(">test_sequence\n")
        f.write("ATCG\n")
        f.write("ATCG\n")
        f.write("ATCG\n")
        temp_path = f.name

    try:
        sequence = load_dna_sequence(temp_path)
        assert sequence == "ATCGATCGATCG"
        assert len(sequence) == 12
    finally:
        import os

        os.unlink(temp_path)
