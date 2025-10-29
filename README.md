# 🧬 DNA-Sec

**Détection de malware dans les séquences ADN** - Outil de cybersécurité pour analyser les fichiers FASTA et GenBank à la recherche de code malveillant encodé.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)](Dockerfile)

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Démarrage rapide](#-démarrage-rapide)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
  - [CLI](#cli---ligne-de-commande)
  - [Interface Web](#interface-web)
  - [Docker](#docker)
- [Comment ça marche](#-comment-ça-marche)
- [Exemples](#-exemples)
- [API Documentation](#-api-documentation)
- [Développement](#-développement)
- [Sécurité](#-sécurité)
- [Dépannage](#-dépannage)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## 📋 Vue d'ensemble

DNA-Sec est un scanner de sécurité qui analyse les séquences ADN pour détecter du code malveillant encodé :

- ✅ **Parse** des fichiers FASTA/GenBank
- ✅ **Décode** l'ADN en données binaires (A=00, C=01, G=10, T=11)
- ✅ **Scanne** avec YARA pour détecter shellcode, exécutables, commandes système
- ✅ **Génère** des rapports JSON avec score de risque
- 🌐 **Interface web** moderne 
- 🐳 **Docker ready** pour déploiement facile

### Cas d'usage

- 🔬 Recherche en biosécurité (détection de séquences encodées)
- 🧪 Analyse forensique de données biologiques synthétiques
- 🎓 Formation en cybersécurité bioinformatique
- 🛡️ Audit de sécurité de bases de données génétiques

---

## 🚀 Démarrage rapide

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/kira-mari/DNA-Sec.git
cd DNA-Sec

# Installer les dépendances
pip install -r requirements.txt

# Installer le package
pip install -e .
```

### Premier scan

```bash
# CLI
dna-sec examples/malicious_dna.fasta --output report.json

# Web (mode DEMO sans YARA)
cd web
python app_demo.py
# Ouvrir http://localhost:5000
```

---

## 📥 Installation

### Prérequis

- **Python 3.8+** (3.11 recommandé)
- **pip** (gestionnaire de packages)
- **(Optionnel)** YARA pour détection avancée

### Installation standard

```bash
# 1. Cloner le repository
git clone https://github.com/kira-mari/DNA-Sec.git
cd DNA-Sec

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

# 3. Installer les dépendances de base
pip install -r requirements.txt

# 4. Installer le package en mode développement
pip install -e .
```

### Installation de YARA (optionnel)

YARA est **optionnel** mais recommandé pour une détection complète. Si YARA n'est pas installé, DNA-Sec utilisera un scanner de fallback.

**Installation de YARA par plateforme :**

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# Méthode 1 : pip (peut nécessiter Visual C++)
pip install yara-python

# Méthode 2 : wheel précompilée
# Télécharger depuis https://github.com/VirusTotal/yara-python/releases
pip install yara_python-4.3.1-cp311-cp311-win_amd64.whl
```
</details>

<details>
<summary><b>🐧 Linux (Ubuntu/Debian)</b></summary>

```bash
# Installer les dépendances système
sudo apt-get update
sudo apt-get install libyara-dev

# Installer le package Python
pip install yara-python
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# Installer YARA via Homebrew
brew install yara

# Installer le package Python
pip install yara-python
```
</details>

### Installation avec Docker

```bash
# Build de l'image
docker-compose build

# Lancer le service
docker-compose up -d

# Accéder à l'interface web
# http://localhost:5000
```

### Configuration

Copier le fichier de configuration d'exemple :

```bash
cp .env.example .env
```

Éditer `.env` selon vos besoins :

```ini
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security Settings
MAX_FILE_SIZE=10485760      # 10MB max
SCAN_TIMEOUT=30             # 30 secondes
CLEANUP_INTERVAL=300        # 5 minutes

# YARA Configuration
USE_YARA=true               # false pour mode fallback

# Rate Limiting
RATE_LIMIT_SCAN=10          # 10 requêtes/minute

# Logging
LOG_LEVEL=INFO
```

---

## 🎯 Utilisation

### CLI - Ligne de commande

```bash
# Scan simple
dna-sec examples/malicious_dna.fasta

# Avec rapport JSON
dna-sec examples/malicious_dna.fasta --output report.json

# Scan de plusieurs fichiers
dna-sec examples/shellcode/shellcode.fasta examples/clean/clean.fasta

# Afficher l'aide
dna-sec --help
```

**Options disponibles :**

```
Usage: dna-sec [OPTIONS] FILE

Options:
  --output PATH  Chemin du fichier de sortie JSON
  --verbose      Affichage détaillé
  --help         Afficher ce message
```

**Exemple de sortie :**

```json
{
  "filename": "malicious_dna.fasta",
  "sequence_length": 1234,
  "risk_score": 90,
  "findings": [
    {
      "frame": 0,
      "offset": 261,
      "rule": "shellcode_x86_common",
      "matched": "X"
    }
  ],
  "recommendation": "⚠️ Séquence suspecte détectée"
}
```

### Interface Web

#### Mode production (avec YARA)

```bash
cd web
python app.py
```

#### Mode DEMO (sans YARA)

```bash
cd web
python app_demo.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

#### Fonctionnalités web

- 📤 **Drag & Drop** de fichiers FASTA/GenBank
- 📊 **Rapport visuel** avec score 
- 🔒 **Sécurité** : timeout 30s, max 10MB, auto-cleanup 5min
- 🚫 **Pas de stockage persistant** (tout en mémoire)

### Docker

#### Docker Compose (recommandé)

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

#### Docker simple

```bash
# Build
docker build -t dna-sec .

# Run
docker run -p 5000:5000 dna-sec

# Avec volumes
docker run -p 5000:5000 \
  -v $(pwd)/examples:/app/examples:ro \
  dna-sec
```

#### Mode production avec nginx

```bash
# Lancer avec le profil production (inclut nginx)
docker-compose --profile production up -d
```

---

## 🧬 Comment ça marche

### 1. Encodage ADN → Binaire

DNA-Sec utilise un encodage par paires de bases :

```
A → 00
C → 01  
G → 10
T → 11
```

**Exemple de décodage :**

```
Séquence ADN : ATCG
Binaire      : 00 11 01 10
Hexadécimal  : 0x3A
ASCII        : ':'
```

Une séquence de 8 bases = 1 octet (byte)

### 2. Détection de patterns malveillants

Le scanner utilise **YARA** pour détecter différents types de menaces :

| Catégorie | Patterns détectés | Exemples |
|-----------|-------------------|----------|
| **Shellcode x86** | Opcodes d'assembleur | `31 C0` (xor eax,eax)<br>`CD 80` (int 0x80)<br>`FF E4` (jmp esp) |
| **Shellcode x64** | Opcodes 64-bit | `48 31 C0` (xor rax,rax)<br>`0F 05` (syscall) |
| **Commandes système** | Strings exécutables | `/bin/sh`<br>`cmd.exe`<br>`powershell` |
| **Injection code** | Patterns dangereux | `eval(`<br>`system(`<br>`exec(` |
| **Headers binaires** | Magic numbers | `7F 45 4C 46` (ELF)<br>`4D 5A` (PE/EXE)<br>`50 4B 03 04` (ZIP) |
| **Polyglots** | Multiformats | Fichiers hybrides |

### 3. Système de scoring

Le **risk_score** est calculé selon la gravité des menaces détectées :

| Score | Niveau | Couleur | Interprétation |
|-------|--------|---------|----------------|
| **0-29** | ✅ Safe | Vert | Séquence sûre, aucune menace |
| **30-49** | 🟡 Low Risk | Jaune | Patterns suspects mineurs |
| **50-79** | 🟠 High Risk | Orange | Menaces potentielles détectées |
| **80-100** | 🔴 Critical | Rouge | Menace critique, ne pas utiliser |

**Calcul du score :**

- Base : 0 points
- +30 points : Shellcode détecté
- +40 points : Header binaire détecté
- +20 points : Commandes système
- +10 points : Patterns injection

### 4. Mode Fallback (sans YARA)

Si YARA n'est pas installé, DNA-Sec utilise un **scanner de fallback** qui détecte :

- ✅ Patterns de shellcode courants (regex sur bytes)
- ✅ Anomalies de contenu GC (>70% ou <30%)
- ✅ Séquences répétitives suspectes
- ⚠️ Moins précis que YARA mais sans dépendances

---

## 📁 Exemples

Le dossier `examples/` contient différents types de séquences pour tester DNA-Sec :

### Clean Sequences (Sûres)

```bash
dna-sec examples/clean/clean.fasta
```

- **Type** : Séquence synthétique sûre
- **Contenu** : Codons répétitifs (ATG, GCA, GGC)
- **GC Content** : ~50-60% (normal)
- **Détection attendue** : ✅ Risk Score 0

### Shellcode x86

```bash
dna-sec examples/shellcode/shellcode.fasta
```

- **Type** : Shellcode Linux pour `/bin/sh`
- **Opcodes** : `31 C0`, `CD 80`, `89 E3`
- **Détection attendue** : 🔴 Risk Score 90, règle `shellcode_x86_common`

### PE Executable

```bash
dna-sec examples/pe_executable/pe.fasta
```

- **Type** : Header d'exécutable Windows
- **Magic Number** : `4D 5A` (MZ)
- **Détection attendue** : 🔴 Risk Score 80, règle `pe_executable`

### ELF Executable

```bash
dna-sec examples/elf_executable/elf.fasta
```

- **Type** : Header d'exécutable Linux
- **Magic Number** : `7F 45 4C 46`
- **Détection attendue** : 🔴 Risk Score 80, règle `elf_executable`

### Command Injection

```bash
dna-sec examples/command_injection/cmd_injection.fasta
```

- **Type** : Commandes shell encodées
- **Strings** : `bash`, `wget`, `curl`
- **Détection attendue** : 🟠 Risk Score 60, règle `command_injection`

### Python Injection

```bash
dna-sec examples/python_injection/py_injection.fasta
```

- **Type** : Code Python malveillant
- **Patterns** : `eval(`, `exec(`, `__import__`
- **Détection attendue** : 🟠 Risk Score 50, règle `python_injection`

### Polyglot Files

```bash
dna-sec examples/polyglot/polyglot.fasta
```

- **Type** : Fichier multi-format (FASTA + ZIP)
- **Headers** : Multiples magic numbers
- **Détection attendue** : 🔴 Risk Score 85, règle `polyglot_file`

---

## 📡 API Documentation

### Endpoints

#### `GET /`
Page d'accueil avec interface web

#### `POST /api/scan`
Analyse un fichier ADN

**Request :**
```http
POST /api/scan HTTP/1.1
Content-Type: multipart/form-data

file=@malicious_dna.fasta
```

**Response (200 OK) :**
```json
{
  "risk_score": 90,
  "filename": "malicious_dna.fasta",
  "sequence_length": 1234,
  "scan_time": 0.456,
  "findings": [
    {
      "frame": 0,
      "offset": 261,
      "rule": "shellcode_x86_common",
      "matched": "X"
    }
  ],
  "recommendation": "⚠️ Séquence suspecte. Ne pas traiter avec des logiciels non durcis."
}
```

**Erreurs :**
- `400 Bad Request` : Fichier invalide, format non supporté
- `408 Request Timeout` : Analyse trop longue (>30s)
- `429 Too Many Requests` : Rate limit dépassé (>10 req/min)
- `500 Internal Server Error` : Erreur serveur

#### `GET /api/health`
Vérification de santé du serveur

**Response :**
```json
{
  "status": "ok",
  "temp_files_count": 0,
  "yara_available": true
}
```

### Rate Limiting

L'API est limitée à **10 requêtes par minute par IP** pour éviter les abus.

**Headers de réponse :**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1635789600
```

---

## 🔧 Développement

### Structure du projet

```
DNA/
├── dna_sec/                    # Package principal
│   ├── __init__.py            # Init du package
│   ├── cli.py                 # Interface CLI (Click)
│   ├── parser.py              # Parser FASTA/GenBank
│   ├── decoder.py             # Décodeur ADN → binaire
│   ├── scanner.py             # Scanner YARA + fallback
│   └── rules/
│       └── malware_in_dna.yar # Règles YARA de détection
├── web/                        # Interface web
│   ├── app.py                 # Serveur Flask (avec YARA)
│   ├── app_demo.py            # Serveur Flask (DEMO sans YARA)
│   ├── templates/
│   │   └── index.html         # Frontend 
│   ├── static/
│   │   └── style.css          # Animations CSS
│   └── uploads/               # Fichiers temporaires
├── examples/                   # Fichiers de test
│   ├── malicious_dna.fasta    # Exemple principal (shellcode)
│   ├── clean/                 # Séquences sûres
│   ├── shellcode/             # Shellcode x86/x64
│   ├── pe_executable/         # Exécutables Windows
│   ├── elf_executable/        # Exécutables Linux
│   ├── command_injection/     # Commandes shell
│   ├── python_injection/      # Code Python malveillant
│   └── polyglot/              # Fichiers multi-format
├── tests/                      # Tests structurés
│   ├── __init__.py            # Init package tests
│   ├── conftest.py            # Fixtures pytest partagées
│   ├── unit/                  # Tests unitaires
│   │   ├── __init__.py
│   │   ├── test_decoder.py   # Tests décodeur
│   │   ├── test_parser.py    # Tests parser
│   │   └── test_scanner.py   # Tests scanner
│   └── integration/           # Tests d'intégration
│       ├── __init__.py
│       └── test_cli.py        # Tests CLI
├── docs/                       # Documentation technique
│   ├── ARCHITECTURE.md        # Architecture détaillée
│   └── INSTALL_YARA.md        # Guide installation YARA
├── .github/                    # CI/CD GitHub Actions
│   └── workflows/
│       └── tests.yml          # Pipeline de tests
├── .env.example               # Configuration d'exemple
├── .editorconfig              # Standards d'édition
├── .gitignore                 # Fichiers à ignorer
├── requirements.txt           # Dépendances Python
├── pytest.ini                 # Configuration pytest
├── setup.py                   # Configuration du package
├── Dockerfile                 # Image Docker
├── docker-compose.yml         # Orchestration Docker
├── Makefile                   # Commandes make (Linux/macOS)
├── tasks.ps1                  # Commandes PowerShell (Windows)
├── start_web.sh               # Script démarrage (Linux/macOS)
├── start_web.ps1              # Script démarrage (Windows)
├── LICENSE                    # Licence MIT
├── CONTRIBUTING.md            # Guide contributeur
└── README.md                  # Ce fichier
```

### Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-cov

# Lancer tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/ -v

# Tests d'intégration seulement
pytest tests/integration/ -v

# Avec couverture de code
pytest --cov=dna_sec --cov-report=html

# Tests spécifiques
pytest tests/unit/test_scanner.py -v

# Tests avec marqueurs
pytest -m "not slow"
```

**Raccourcis avec tasks.ps1 (Windows)** :
```powershell
.\tasks.ps1 test              # Tous les tests
.\tasks.ps1 test-unit         # Tests unitaires
.\tasks.ps1 test-integration  # Tests intégration
.\tasks.ps1 coverage          # Tests avec couverture
```

**Raccourcis avec Makefile (Linux/macOS)** :
```bash
make test              # Tous les tests
make test-unit         # Tests unitaires
make test-integration  # Tests intégration
make coverage          # Tests avec couverture
```

**Couverture actuelle :**
- `decoder.py` : 95%
- `parser.py` : 90%
- `scanner.py` : 85%
- `cli.py` : 80%

### Ajouter des règles YARA

Éditez `dna_sec/rules/malware_in_dna.yar` :

```yara
rule my_custom_rule {
    meta:
        description = "Ma règle personnalisée"
        author = "Votre nom"
        severity = "high"
        
    strings:
        $pattern1 = { 48 65 6C 6C 6F }  // "Hello" en hex
        $pattern2 = "malicious_string"
        
    condition:
        any of them
}
```

Tester votre règle :

```bash
dna-sec examples/your_test.fasta --verbose
```

### Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python | 3.8+ |
| CLI | Click | 8.0+ |
| Web Framework | Flask | 2.3+ |
| Bio Parser | BioPython | 1.80+ |
| Pattern Matching | YARA | 4.3+ (optionnel) |
| Frontend CSS | Tailwind CSS | 3.x |
| Frontend JS | Alpine.js | 3.x |
| Containerization | Docker | 20.10+ |
| Testing | Pytest | 7.x |

---

## 🔐 Sécurité

### Mesures de sécurité implémentées

#### API Web

- ✅ **Validation stricte** : Seuls `.fasta`, `.fa`, `.fna`, `.gb`, `.gbk` acceptés
- ✅ **Limite de taille** : 10MB maximum par fichier
- ✅ **Timeout** : 30 secondes maximum par scan
- ✅ **Auto-cleanup** : Fichiers supprimés après 5 minutes
- ✅ **Rate limiting** : 10 requêtes/minute par IP
- ✅ **Pas de stockage persistant** : Tout en mémoire
- ✅ **Isolation** : Chaque scan est isolé

#### Docker

- ✅ **Utilisateur non-root** : `dna-sec` (uid 1000)
- ✅ **Image minimale** : Python 3.11-slim
- ✅ **Health checks** : Surveillance automatique
- ✅ **Limites de ressources** : CPU et mémoire contrôlés

#### YARA

- ✅ **Optionnel** : Fallback si non installé
- ✅ **Règles validées** : Pas d'exécution de code
- ✅ **Timeout** : Évite les boucles infinies

### Signaler une vulnérabilité

**Ne créez PAS d'issue publique** pour les vulnérabilités de sécurité.

Envoyez un email à : **[VOTRE_EMAIL]** avec :
- Description de la vulnérabilité
- Étapes pour reproduire
- Impact potentiel
- Suggestions de correction (si possible)

---

## 🐛 Dépannage

### Erreur `dna-sec: command not found`

**Cause** : Le package n'est pas installé

**Solution** :
```bash
pip install -e .
```

Ou utilisez le module directement :
```bash
python -m dna_sec.cli examples/malicious_dna.fasta
```

### Erreur `libyara.dll not found` (Windows)

**Cause** : YARA n'est pas installé ou mal configuré

**Solution 1** : Mode DEMO sans YARA
```bash
cd web
python app_demo.py
```

**Solution 2** : Installer YARA avec wheel précompilée
```bash
# Télécharger depuis https://github.com/VirusTotal/yara-python/releases
pip install yara_python-4.3.1-cp311-cp311-win_amd64.whl
```

**Solution 3** : Installer Visual C++ Build Tools
1. Télécharger [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/)
2. Installer "C++ build tools"
3. `pip install yara-python`

### Erreur `Bases invalides trouvées dans la séquence`

**Cause** : Le fichier FASTA contient des caractères non-ADN

**Solution** : Vérifiez que votre fichier ne contient que `A`, `T`, `C`, `G`

Caractères invalides courants :
- `N` (base ambiguë)
- `.` `-` (gaps)
- `U` (RNA - remplacer par T)

Nettoyage automatique :
```bash
# Remplacer N par A
sed 's/N/A/g' input.fasta > clean.fasta
```

### Erreur `Port 5000 already in use`

**Cause** : Le port 5000 est utilisé par un autre processus

**Solution** :
```bash
# Modifier le port dans web/app.py
app.run(host='0.0.0.0', port=8080, debug=False)
```

Ou tuer le processus :
```bash
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process

# Linux/macOS
lsof -ti:5000 | xargs kill
```

### Erreur `Module 'Bio' not found`

**Cause** : BioPython n'est pas installé

**Solution** :
```bash
pip install biopython
```

### Tests qui échouent

**Cause** : Dépendances de test manquantes

**Solution** :
```bash
pip install pytest pytest-cov
pytest tests/
```

### Docker build échoue

**Cause** : Problème de dépendances ou de permissions

**Solution** :
```bash
# Nettoyer le cache Docker
docker system prune -a

# Rebuild sans cache
docker-compose build --no-cache
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour :

- 📋 Setup de l'environnement de développement
- 🎨 Standards de code et style
- ✅ Guide de tests
- 📝 Process de Pull Request
- 🐛 Template de rapport de bug

### Quick Start Contribution

```bash
# 1. Forker le projet sur GitHub
# 2. Cloner votre fork
git clone https://github.com/VOTRE_USERNAME/DNA-Sec.git

# 3. Créer une branche
git checkout -b feature/ma-fonctionnalite

# 4. Développer et tester
pytest tests/

# 5. Committer
git commit -m "feat: ajout de fonctionnalité X"

# 6. Pousser
git push origin feature/ma-fonctionnalite

# 7. Ouvrir une Pull Request
```


## ⚠️ Avertissement

**DNA-Sec** est un outil conçu à des fins **éducatives et de recherche** en biosécurité.

- ⚠️ Ne pas utiliser pour analyser des données sensibles sans mesures de sécurité appropriées
- ⚠️ Les séquences détectées comme "malveillantes" peuvent être des faux positifs
- ⚠️ Cet outil ne remplace pas une analyse de sécurité professionnelle
- ⚠️ Utiliser uniquement dans des environnements contrôlés

---

<div align="center">

**🧬 DNA-Sec v0.1.0**

*Secure DNA Malware Detection*

Made with 💚 and ⚡

[![GitHub](https://img.shields.io/badge/GitHub-DNA--Sec-181717?logo=github)](https://github.com/kira-mari/DNA-Sec)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python)](https://python.org)

</div>
