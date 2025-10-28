# Contributing to DNA-Sec

Merci de votre intérêt pour contribuer à DNA-Sec ! 🧬

## Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Pull Requests](#pull-requests)
- [Signaler des bugs](#signaler-des-bugs)

## Code de conduite

En participant à ce projet, vous acceptez de respecter les autres contributeurs et de maintenir un environnement collaboratif et inclusif.

## Comment contribuer

Il existe plusieurs façons de contribuer :

1. **Signaler des bugs** : Ouvrez une issue avec des détails précis
2. **Proposer des fonctionnalités** : Discutez d'abord via une issue
3. **Améliorer la documentation** : README, docstrings, exemples
4. **Soumettre du code** : Corrections de bugs, nouvelles fonctionnalités

## Configuration de l'environnement

### Prérequis

- Python 3.8+
- Git
- (Optionnel) Docker

### Installation pour le développement

```bash
# 1. Forker et cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/DNA.git
cd DNA

# 2. Créer un environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# 3. Installer les dépendances de développement
pip install -r requirements-full.txt
pip install -e .

# 4. Installer les outils de développement
pip install pytest pytest-cov black flake8 mypy

# 5. Copier la configuration d'exemple
cp .env.example .env
```

### Installation de YARA (optionnel)

YARA est optionnel mais recommandé pour un scan complet :

**Windows :**
```bash
pip install yara-python
```

Si vous rencontrez des erreurs DLL, téléchargez les binaires depuis [VirusTotal/YARA](https://github.com/VirusTotal/yara/releases).

**Linux (Ubuntu/Debian) :**
```bash
sudo apt-get install libyara-dev
pip install yara-python
```

**macOS :**
```bash
brew install yara
pip install yara-python
```

## Standards de code

### Style Python

Nous suivons [PEP 8](https://pep8.org/) avec quelques ajustements :

- **Longueur de ligne** : 100 caractères maximum
- **Formatage** : Utilisez `black` pour formater automatiquement
- **Imports** : Triés alphabétiquement, groupés (standard, externes, locaux)
- **Docstrings** : Format Google pour les fonctions publiques

### Exemple de docstring

```python
def scan_dna_for_malware(sequence: str, rules_file: str = None) -> dict:
    """
    Scanne une séquence ADN pour détecter des patterns malveillants.
    
    Args:
        sequence: La séquence ADN à analyser (A, T, C, G)
        rules_file: Chemin vers le fichier de règles YARA (optionnel)
        
    Returns:
        dict: Résultats du scan avec clés 'is_malicious', 'matches', 'metadata'
        
    Raises:
        ValueError: Si la séquence contient des caractères invalides
        
    Example:
        >>> result = scan_dna_for_malware("ATCGATCG")
        >>> result['is_malicious']
        False
    """
    pass
```

### Vérifications avant commit

```bash
# Formater le code
black dna_sec/ tests/

# Vérifier le style
flake8 dna_sec/ tests/ --max-line-length=100

# Vérifier les types
mypy dna_sec/

# Lancer les tests
pytest tests/ -v --cov=dna_sec
```

## Tests

### Structure des tests

```
tests/
├── test_decoder.py     # Tests du décodeur binaire
├── test_parser.py      # Tests du parser FASTA/GenBank
├── test_scanner.py     # Tests du scanner YARA
└── test_cli.py         # Tests de l'interface CLI
```

### Exécuter les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=dna_sec --cov-report=html

# Tests spécifiques
pytest tests/test_scanner.py -v

# Tests avec marqueurs
pytest -m "not slow"
```

### Écrire de nouveaux tests

- **Nommage** : `test_<fonction>_<cas>`
- **Organisation** : Un fichier de test par module
- **Couverture** : Visez >80% de couverture de code
- **Fixtures** : Utilisez pytest fixtures pour les données de test

Exemple :

```python
import pytest
from dna_sec.parser import load_fasta

@pytest.fixture
def sample_fasta_file(tmp_path):
    """Crée un fichier FASTA temporaire pour les tests."""
    fasta_file = tmp_path / "sample.fasta"
    fasta_file.write_text(">sequence1\nATCGATCG\n")
    return str(fasta_file)

def test_load_fasta_valid(sample_fasta_file):
    """Teste le chargement d'un fichier FASTA valide."""
    result = load_fasta(sample_fasta_file)
    assert "sequence1" in result
    assert result["sequence1"] == "ATCGATCG"
```

## Pull Requests

### Processus

1. **Créer une branche** depuis `main`
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```

2. **Développer et tester**
   - Écrivez du code propre et testé
   - Ajoutez des tests pour vos modifications
   - Mettez à jour la documentation si nécessaire

3. **Committer** avec des messages clairs
   ```bash
   git commit -m "feat: ajout du support GenBank complet"
   ```

   Format des messages de commit :
   - `feat:` Nouvelle fonctionnalité
   - `fix:` Correction de bug
   - `docs:` Documentation
   - `test:` Ajout/modification de tests
   - `refactor:` Refactoring sans changement de comportement
   - `perf:` Amélioration de performance
   - `chore:` Tâches de maintenance

4. **Pousser** vers votre fork
   ```bash
   git push origin feature/ma-fonctionnalite
   ```

5. **Ouvrir une Pull Request**
   - Titre descriptif
   - Description détaillée des changements
   - Référence aux issues concernées (`Fixes #123`)
   - Screenshots pour les changements UI

### Checklist PR

Avant de soumettre, vérifiez que :

- [ ] Le code suit les standards de style (black, flake8)
- [ ] Tous les tests passent (`pytest`)
- [ ] La couverture de code est maintenue/améliorée
- [ ] La documentation est mise à jour
- [ ] Les commits ont des messages descriptifs
- [ ] Pas de conflits avec `main`
- [ ] Les changements sont testés localement

## Signaler des bugs

### Template d'issue

```markdown
**Description du bug**
Une description claire et concise du bug.

**Comment reproduire**
1. Aller sur '...'
2. Cliquer sur '...'
3. Exécuter '...'
4. Voir l'erreur

**Comportement attendu**
Ce qui devrait se passer normalement.

**Comportement actuel**
Ce qui se passe actuellement.

**Environnement**
- OS: [Windows 10, Ubuntu 22.04, macOS 13]
- Python: [3.11.0]
- DNA-Sec: [0.1.0]
- YARA installé: [Oui/Non]

**Logs/Screenshots**
```
Si applicable, ajoutez des logs ou captures d'écran.
```

**Contexte additionnel**
Toute autre information pertinente.
```

### Signaler une vulnérabilité de sécurité

**Ne créez PAS d'issue publique** pour les vulnérabilités de sécurité.

Envoyez un email à : [VOTRE_EMAIL] avec :
- Description de la vulnérabilité
- Étapes pour reproduire
- Impact potentiel
- Suggestions de correction (si possible)

## Bonnes pratiques

### Performance

- Évitez les boucles imbriquées sur de grandes séquences
- Utilisez des générateurs pour les gros fichiers
- Profilez le code avec `cProfile` si nécessaire

### Sécurité

- Validez toujours les entrées utilisateur
- Sanitisez les chemins de fichiers
- Limitez la taille des fichiers uploadés
- Ne committez jamais de secrets (.env dans .gitignore)

### Documentation

- Commentez le "pourquoi", pas le "quoi"
- Mettez à jour le README pour les nouvelles fonctionnalités
- Ajoutez des exemples d'utilisation
- Documentez les limitations connues

## Questions ?

- Ouvrez une issue avec le tag `question`
- Consultez la documentation existante
- Vérifiez les issues fermées

## Remerciements

Merci de contribuer à DNA-Sec ! Votre aide rend ce projet meilleur pour tous. 🙏
