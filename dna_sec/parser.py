from Bio import SeqIO
from pathlib import Path


def load_dna_sequence(file_path: str) -> str:
    """
    Charge une séquence d'ADN depuis un fichier FASTA ou GenBank.

    Args:
        file_path (str): Chemin vers le fichier.

    Returns:
        str: Séquence d'ADN en majuscules (A, T, C, G).

    Raises:
        ValueError: Si le format n'est pas supporté ou la séquence est vide.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé : {file_path}")

    # Déterminer le format
    suffix = file_path.suffix.lower()
    if suffix in [".fa", ".fasta", ".fna"]:
        fmt = "fasta"
    elif suffix in [".gb", ".gbk", ".genbank"]:
        fmt = "genbank"
    else:
        raise ValueError("Format non supporté. Utilisez .fasta ou .genbank.")

    records = list(SeqIO.parse(file_path, fmt))
    if not records:
        raise ValueError("Aucune séquence trouvée dans le fichier.")

    # Concaténer toutes les séquences (cas multi-record)
    full_seq = "".join(str(record.seq).upper() for record in records)

    # Valider les caractères
    valid_bases = set("ATCG")
    if not set(full_seq).issubset(valid_bases):
        invalid = set(full_seq) - valid_bases
        raise ValueError(f"Bases invalides trouvées : {invalid}")

    return full_seq
