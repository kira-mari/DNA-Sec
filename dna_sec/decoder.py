def dna_to_binary(dna_seq: str) -> bytes:
    """
    Convertit une séquence d'ADN en données binaires.
    Mapping : A=00, C=01, G=10, T=11

    Args:
        dna_seq (str): Séquence ADN (A, T, C, G)

    Returns:
        bytes: Données binaires décodées.
    """
    mapping = {"A": "00", "C": "01", "G": "10", "T": "11"}
    binary_str = "".join(mapping[base] for base in dna_seq)

    # Remplir pour que la longueur soit multiple de 8
    padding = len(binary_str) % 8
    if padding:
        binary_str += "0" * (8 - padding)

    # Convertir en bytes
    byte_array = bytearray()
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i : i + 8]
        byte_array.append(int(byte, 2))

    return bytes(byte_array)


def reverse_complement(dna_seq: str) -> str:
    """Retourne le complément inverse d'une séquence d'ADN."""
    complement = str.maketrans("ATCG", "TAGC")
    return dna_seq.translate(complement)[::-1]


def get_all_reading_frames(dna_seq: str):
    """
    Génère les 6 cadres de lecture :
    - 3 forward (décalage 0, 1, 2)
    - 3 reverse-complement (décalage 0, 1, 2)
    """
    frames = []
    # Forward
    for i in range(3):
        frames.append(dna_seq[i:])
    # Reverse complement
    rev_comp = reverse_complement(dna_seq)
    for i in range(3):
        frames.append(rev_comp[i:])
    return frames
