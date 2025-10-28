# Architecture DNA-Sec

## Vue d'ensemble

DNA-Sec est un outil de détection de malware dans les séquences ADN, composé de plusieurs modules indépendants qui travaillent ensemble.

## Architecture globale

```
┌─────────────────────────────────────────────────┐
│              Interface Utilisateur              │
├──────────────────┬──────────────────────────────┤
│   CLI (Click)    │    Web (Flask)               │
└────────┬─────────┴──────────┬───────────────────┘
         │                     │
         └─────────┬───────────┘
                   │
         ┌─────────▼─────────┐
         │   DNA-Sec Core    │
         │   (dna_sec/)      │
         └─────────┬─────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼────┐    ┌───▼────┐
│Parser │    │ Decoder │    │Scanner │
└───────┘    └─────────┘    └────┬───┘
                                  │
                            ┌─────▼──────┐
                            │ YARA Rules │
                            └────────────┘
```

## Modules principaux

### 1. Parser (`parser.py`)

**Rôle** : Charger et valider les fichiers FASTA/GenBank

**Fonctions** :
- `load_fasta(filepath)` : Parse fichier FASTA
- `load_genbank(filepath)` : Parse fichier GenBank
- `validate_sequence(seq)` : Vérifie que seuls A,T,C,G sont présents

**Dépendances** : BioPython

**Flow** :
```
Fichier → BioPython SeqIO → Validation → Dict {id: sequence}
```

### 2. Decoder (`decoder.py`)

**Rôle** : Convertir ADN en données binaires

**Mapping** :
```python
A → 00
C → 01
G → 10
T → 11
```

**Fonctions** :
- `dna_to_binary(sequence)` : ADN → bytes
- `get_all_reading_frames(sequence)` : Génère 6 cadres de lecture

**Exemple** :
```
ATCG → 00 11 01 10 → 0x3A → ':'
```

### 3. Scanner (`scanner.py`)

**Rôle** : Détecter les patterns malveillants

**Modes** :
1. **Mode YARA** (si disponible) :
   - Charge les règles depuis `rules/malware_in_dna.yar`
   - Scan binaire avec yara.match()
   - Détection précise de shellcode, headers, commandes

2. **Mode Fallback** (sans YARA) :
   - Détection de patterns simples par regex
   - Analyse statistique (contenu GC)
   - Moins précis mais sans dépendances

**Fonctions** :
- `scan_dna_for_malware(sequence)` : Point d'entrée principal
- `_mock_scan(sequence)` : Scanner de secours
- `get_shellcode_explanation(hex)` : Explications pédagogiques
- `get_header_explanation(hex)` : Explications headers

**Output** :
```python
{
    "risk_score": int,      # 0-100
    "findings": list,       # Détails des menaces
    "recommendation": str   # Conseil de sécurité
}
```

### 4. CLI (`cli.py`)

**Rôle** : Interface ligne de commande

**Framework** : Click

**Commandes** :
```bash
dna-sec <fichier> [--output report.json]
```

**Flow** :
```
Args → Parser → Decoder → Scanner → JSON/Console
```

### 5. Web (`web/app.py` et `web/app_demo.py`)

**Rôle** : Interface web avec API REST

**Framework** : Flask

**Endpoints** :
- `GET /` : Page HTML
- `POST /api/scan` : Upload et scan
- `GET /api/health` : Health check

**Sécurité** :
- Validation des extensions (.fasta, .fa, .gb, .gbk)
- Limite de taille : 10MB
- Timeout : 30 secondes
- Rate limiting : 10 req/min par IP
- Auto-cleanup : 5 minutes

**Flow** :
```
Upload → Validation → Save temp → Scan → JSON → Cleanup
```

## Règles YARA (`rules/malware_in_dna.yar`)

### Types de détection

1. **Shellcode x86/x64**
   - Opcodes : `31 C0`, `CD 80`, `FF E4`, `48 31 C0`, `0F 05`
   - Syscalls Linux/Windows
   - Jump instructions

2. **Chaînes exécutables**
   - `/bin/sh`, `cmd.exe`, `powershell`
   - `eval(`, `exec(`, `system(`
   - `bash`, `wget`, `curl`

3. **Headers binaires**
   - ELF : `7F 45 4C 46`
   - PE : `4D 5A`
   - ZIP : `50 4B 03 04`

4. **Polyglots**
   - Fichiers multi-format
   - Embedded archives

### Structure d'une règle

```yara
rule shellcode_x86_common {
    meta:
        description = "Shellcode x86 courant"
        severity = "critical"
        
    strings:
        $opcode1 = { 31 C0 }  // xor eax, eax
        $opcode2 = { CD 80 }  // int 0x80
        
    condition:
        any of them
}
```

## Système de scoring

### Calcul du risk_score

```python
if "shellcode" in rule:
    score = 90
elif "binary_headers" in rule:
    score = 80
elif "executable_strings" in rule:
    score = 70
elif "polyglot" in rule:
    score = 85
else:
    score = 50
```

### Interprétation

| Score | Niveau | Action |
|-------|--------|--------|
| 0-29 | Safe | Utilisation sûre |
| 30-49 | Low | Vérification recommandée |
| 50-79 | High | Analyse approfondie |
| 80-100 | Critical | Ne pas utiliser |

## Flow de données complet

### Scan CLI

```
1. User: dna-sec file.fasta
2. CLI: Parse arguments
3. Parser: Load FASTA → {id: seq}
4. Decoder: seq → binary frames (6 frames)
5. Scanner: YARA match on each frame
6. Scanner: Build findings list
7. Scanner: Calculate risk_score
8. CLI: Format output (JSON/console)
9. User: Receive report
```

### Scan Web

```
1. User: Upload file via /api/scan
2. Flask: Validate file (ext, size)
3. Flask: Check rate limit
4. Flask: Save to temp (web/uploads/)
5. Parser: Load sequence
6. Decoder: seq → binary
7. Scanner: Detect threats
8. Flask: Format JSON response
9. Flask: Schedule cleanup (5min)
10. User: Receive JSON
```

## Gestion des erreurs

### Parser
- `ValueError` : Bases invalides dans séquence
- `FileNotFoundError` : Fichier introuvable
- `SeqIO error` : Format FASTA/GB invalide

### Scanner
- `ImportError` : YARA non disponible → Fallback
- `yara.Error` : Règles invalides → Fallback
- `TimeoutError` : Scan trop long → Abort

### Web
- `400` : Fichier invalide
- `408` : Timeout
- `429` : Rate limit
- `500` : Erreur serveur

## Performance

### Optimisations

1. **Lecture streaming** : Pas de chargement complet en RAM
2. **Cache YARA** : Règles compilées une seule fois
3. **Frames parallèles** : Scan simultané (futur)
4. **Cleanup async** : Suppression en background

### Limites

- **Taille max** : 10MB (web), illimité (CLI)
- **Timeout** : 30s (web), illimité (CLI)
- **Rate limit** : 10/min (web), aucun (CLI)

## Sécurité

### Mesures implémentées

1. **Input validation** : Extensions, taille, contenu
2. **Isolation** : Pas d'exécution de code
3. **Sandboxing** : YARA scan only, no exec
4. **Cleanup** : Auto-suppression fichiers temp
5. **Rate limiting** : Protection DDoS
6. **No persistence** : Pas de stockage long terme

### Threat model

**Risques couverts** :
- ✅ Upload de fichiers malveillants
- ✅ DDoS par upload massif
- ✅ Path traversal
- ✅ Buffer overflow (Python protégé)

**Risques non couverts** :
- ⚠️ Zero-day dans BioPython
- ⚠️ YARA rule exploitation (théorique)

## Testing

### Structure

```
tests/
├── conftest.py           # Fixtures partagées
├── unit/                 # Tests modules isolés
│   ├── test_parser.py
│   ├── test_decoder.py
│   └── test_scanner.py
└── integration/          # Tests end-to-end
    └── test_cli.py
```

### Coverage cible

- Parser : 95%
- Decoder : 95%
- Scanner : 85% (mode YARA difficile à tester)
- CLI : 80%

## Déploiement

### Docker

**Image** : Python 3.11-slim
**User** : non-root (dna-sec, uid 1000)
**Port** : 5000
**Health** : GET /api/health

**Volumes** :
- `examples/` : Read-only
- `uploads/` : Ephemeral

### Production

**Recommandations** :
1. Nginx reverse proxy (HTTPS)
2. Gunicorn workers (4+)
3. Redis pour rate limiting
4. Monitoring (Prometheus)
5. Logs centralisés (ELK)

## Évolutions futures

### Roadmap

1. **v0.2** :
   - Support RNA (U au lieu de T)
   - Export rapport PDF
   - API GraphQL

2. **v0.3** :
   - ML pour détection anomalies
   - Scan parallèle multi-core
   - Support GenBank complet

3. **v1.0** :
   - Base de données PostgreSQL
   - Authentification users
   - Dashboard analytics
   - Plugins YARA custom

## Références

- [YARA Documentation](https://yara.readthedocs.io/)
- [BioPython Tutorial](https://biopython.org/DIST/docs/tutorial/Tutorial.html)
- [Flask Best Practices](https://flask.palletsprojects.com/)
- [DNA Computing](https://en.wikipedia.org/wiki/DNA_computing)
