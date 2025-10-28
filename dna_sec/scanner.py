try:
    import yara

    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False
    print("[ATTENTION] YARA non disponible - Fonctionnalites de scan limitees")

import os
from .decoder import dna_to_binary, get_all_reading_frames

# Chemin vers les règles YARA
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules", "malware_in_dna.yar")


def get_shellcode_explanation(hex_str: str) -> str:
    """Retourne une explication pédagogique pour les opcodes shellcode x86"""
    explanations = {
        "31C0": "xor eax, eax → Met le registre EAX à zéro",
        "31DB": "xor ebx, ebx → Met le registre EBX à zéro",
        "31C9": "xor ecx, ecx → Met le registre ECX à zéro",
        "31D2": "xor edx, edx → Met le registre EDX à zéro",
        "6A0B": "push 0x0B → Empile la valeur 11 (syscall execve)",
        "58": "pop eax → Récupère une valeur dans EAX",
        "CD80": "int 0x80 → Appel système Linux (exécute syscall)",
        "FFE4": "jmp esp → Saute à l'adresse dans ESP (technique d'exploitation)",
    }

    # Chercher des patterns connus
    for pattern, explanation in explanations.items():
        if pattern in hex_str.upper():
            return f"Opcode {pattern}: {explanation}"

    return f"Signature inconnue: {hex_str[:16]}..."


def _mock_scan(dna_seq: str) -> dict:
    """
    Scanner de secours quand YARA n'est pas disponible.
    Détecte des patterns simples sans dépendances.
    """
    findings = []
    risk_score = 0

    # Recherche de patterns simples
    patterns = {
        "ATGATGATGATG": ("Répétition ATG suspecte", "medium", 30),
        "TCCTTTCT": ("Pattern shellcode potentiel", "high", 70),
        "AAAAAAAAAA": ("Séquence NOP-like", "medium", 40),
    }

    for pattern, (desc, severity, score) in patterns.items():
        if pattern in dna_seq:
            findings.append(
                {
                    "frame": 0,
                    "offset": dna_seq.index(pattern),
                    "rule": "pattern_detection",
                    "matched_hex": pattern,
                    "matched_ascii": None,
                    "dna_snippet": pattern,
                    "severity": severity,
                    "explanation": desc,
                    "impact": "Détection basique sans YARA",
                    "technical_detail": f"Pattern trouvé: {pattern}",
                }
            )
            risk_score = max(risk_score, score)

    # Analyse statistique
    if len(dna_seq) > 0:
        gc_content = (dna_seq.count("G") + dna_seq.count("C")) / len(dna_seq)
        if gc_content > 0.7 or gc_content < 0.3:
            findings.append(
                {
                    "frame": 0,
                    "offset": 0,
                    "rule": "gc_anomaly",
                    "severity": "low",
                    "explanation": f"Contenu GC anormal: {gc_content*100:.1f}%",
                    "impact": "Possible encodage binaire",
                    "technical_detail": f"GC: {gc_content*100:.1f}% (normal: 40-60%)",
                }
            )
            risk_score = max(risk_score, 20)

    if risk_score > 0:
        recommendation = "⚠️  Analyse limitée sans YARA - Installer yara-python pour scan complet"
    elif not findings:
        recommendation = "Séquence saine (scan basique sans YARA)"
    else:
        recommendation = "Patterns suspects détectés - Installer YARA pour analyse approfondie"

    return {
        "risk_score": risk_score,
        "findings": findings,
        "recommendation": recommendation,
        "scanner_mode": "basic (no YARA)",
    }


def get_header_explanation(hex_str: str) -> str:
    """Retourne une explication pédagogique pour les headers de fichiers"""
    headers = {
        "7F454C46": "ELF Header → Exécutable Linux/Unix",
        "4D5A": "MZ Header → Exécutable Windows (PE/DOS)",
        "504B0304": "ZIP Header → Archive compressée (peut contenir malware)",
    }

    hex_upper = hex_str.upper()
    for pattern, explanation in headers.items():
        if pattern in hex_upper:
            return explanation

    return f"Signature binaire: {hex_str[:16]}..."


def scan_dna_for_malware(dna_seq: str) -> dict:
    """
    Analyse une séquence d'ADN pour détecter du malware.
    Fonctionne avec ou sans YARA.

    Returns:
        dict: Rapport de scan avec score et anomalies.
    """
    if not YARA_AVAILABLE:
        return _mock_scan(dna_seq)

    try:
        rules = yara.compile(filepath=RULES_PATH)
    except Exception as e:
        print(f"⚠️  Erreur YARA: {e}")
        return _mock_scan(dna_seq)

    frames = get_all_reading_frames(dna_seq)
    findings = []
    max_score = 0

    for i, frame in enumerate(frames):
        if len(frame) < 8:
            continue
        try:
            binary_data = dna_to_binary(frame)
        except Exception:
            continue

        matches = rules.match(data=binary_data)
        for match in matches:
            for string_match in match.strings:
                offset = string_match.instances[0].offset if string_match.instances else 0
                matched_data = (
                    string_match.instances[0].matched_data if string_match.instances else b""
                )

                # Convertir en hex pour affichage
                matched_hex = matched_data.hex().upper() if matched_data else ""

                # Essayer de décoder en ASCII
                try:
                    readable = matched_data.decode("ascii", errors="ignore")
                except Exception:
                    readable = ""

                # Extraire la portion ADN correspondante (approximatif)
                dna_start = offset * 4  # Chaque byte = 4 bases ADN
                dna_end = dna_start + len(matched_data) * 4
                dna_snippet = (
                    frame[dna_start:dna_end]
                    if dna_end <= len(frame)
                    else frame[dna_start : dna_start + 20]
                )

                # Créer un finding enrichi
                finding = {
                    "frame": i,
                    "offset": offset,
                    "rule": match.rule,
                    "matched_hex": matched_hex[:40],  # Limiter à 40 chars
                    "matched_ascii": readable[:50] if readable else None,
                    "dna_snippet": dna_snippet[:40] if dna_snippet else None,
                    "matched_bytes": len(matched_data),
                }

                # Ajouter des explications pédagogiques selon la règle
                if "shellcode" in match.rule.lower():
                    finding["severity"] = "critical"
                    finding["explanation"] = "Code machine x86 détecté (instructions assembleur)"
                    finding["impact"] = "Peut exécuter des commandes arbitraires sur le système"
                    finding["technical_detail"] = get_shellcode_explanation(matched_hex)
                elif "executable_strings" in match.rule.lower():
                    finding["severity"] = "high"
                    finding["explanation"] = "Chaîne de commande système détectée"
                    finding["impact"] = "Peut lancer des programmes ou scripts malveillants"
                    finding["technical_detail"] = (
                        f"Commande: {readable}" if readable else "Chaîne exécutable"
                    )
                elif "binary_headers" in match.rule.lower():
                    finding["severity"] = "high"
                    finding["explanation"] = "Signature de fichier exécutable détectée"
                    finding["impact"] = "Contient probablement un programme compilé caché"
                    finding["technical_detail"] = get_header_explanation(matched_hex)
                else:
                    finding["severity"] = "medium"
                    finding["explanation"] = "Pattern suspect détecté"
                    finding["impact"] = "Comportement anormal dans la séquence"
                    finding["technical_detail"] = f"Pattern: {matched_hex}"

                findings.append(finding)
                # Score basé sur la règle
                if "shellcode" in match.rule:
                    max_score = max(max_score, 90)
                elif "executable_strings" in match.rule:
                    max_score = max(max_score, 70)
                elif "binary_headers" in match.rule:
                    max_score = max(max_score, 80)

    risk_score = min(max_score, 100)
    return {
        "risk_score": risk_score,
        "findings": findings,
        "recommendation": (
            "Séquence suspecte. Ne pas traiter avec des logiciels non durcis."
            if risk_score > 50
            else "Aucune menace détectée."
        ),
    }
