# Installation de YARA

YARA est **optionnel** pour DNA-Sec. Le projet fonctionne sans YARA en utilisant un scanner de fallback, mais YARA offre une détection plus précise et complète.

## 🪟 Windows

### Méthode 1 : Wheel précompilée (Recommandée)

La méthode la plus simple sur Windows :

```powershell
# 1. Télécharger la wheel depuis GitHub
# https://github.com/VirusTotal/yara-python/releases

# 2. Installer la wheel (adapter la version)
pip install yara_python-4.3.1-cp311-cp311-win_amd64.whl
```

**Trouver la bonne wheel** :
- `cp311` = Python 3.11
- `cp310` = Python 3.10
- `win_amd64` = Windows 64-bit
- `win32` = Windows 32-bit

### Méthode 2 : Compilation avec Visual Studio

Si vous avez Visual Studio Build Tools :

```powershell
# 1. Installer Visual Studio Build Tools
# https://visualstudio.microsoft.com/downloads/
# Sélectionner "C++ build tools"

# 2. Installer YARA Python
pip install yara-python
```

### Méthode 3 : Binaires officiels + Python binding

```powershell
# 1. Télécharger YARA binaires depuis
# https://github.com/VirusTotal/yara/releases

# 2. Extraire dans C:\yara\

# 3. Ajouter au PATH
$env:PATH += ";C:\yara"

# 4. Installer le binding Python
pip install yara-python
```

### Vérification

```powershell
python -c "import yara; print(yara.__version__)"
```

Si succès, vous verrez la version (ex: `4.3.1`)

### Problèmes courants

**Erreur : "Unable to find vcvarsall.bat"**
→ Installer Visual Studio Build Tools

**Erreur : "libyara.dll not found"**
→ Télécharger la wheel précompilée (Méthode 1)

**Erreur : "Microsoft Visual C++ 14.0 is required"**
→ Installer Visual C++ Redistributable
→ https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 🐧 Linux (Ubuntu/Debian)

### Installation avec apt

```bash
# 1. Installer les dépendances système
sudo apt-get update
sudo apt-get install -y libyara-dev

# 2. Installer le package Python
pip install yara-python
```

### Installation depuis les sources

```bash
# 1. Installer les outils de build
sudo apt-get install -y automake libtool make gcc pkg-config

# 2. Télécharger et compiler YARA
wget https://github.com/VirusTotal/yara/archive/v4.3.1.tar.gz
tar -xzf v4.3.1.tar.gz
cd yara-4.3.1
./bootstrap.sh
./configure
make
sudo make install

# 3. Mettre à jour ldconfig
sudo ldconfig

# 4. Installer le binding Python
pip install yara-python
```

### Vérification

```bash
python3 -c "import yara; print(yara.__version__)"
yara --version
```

---

## 🍎 macOS

### Installation avec Homebrew

```bash
# 1. Installer YARA via Homebrew
brew install yara

# 2. Installer le package Python
pip3 install yara-python
```

### Installation depuis les sources

```bash
# 1. Installer Xcode Command Line Tools
xcode-select --install

# 2. Télécharger et compiler YARA
wget https://github.com/VirusTotal/yara/archive/v4.3.1.tar.gz
tar -xzf v4.3.1.tar.gz
cd yara-4.3.1
./bootstrap.sh
./configure
make
sudo make install

# 3. Installer le binding Python
pip3 install yara-python
```

### Vérification

```bash
python3 -c "import yara; print(yara.__version__)"
yara --version
```

---

## 🐳 Docker

Si vous utilisez Docker, YARA peut être installé dans l'image :

```dockerfile
# Ajoutez au Dockerfile
FROM python:3.11-slim

# Installer YARA
RUN apt-get update && \
    apt-get install -y libyara-dev && \
    pip install yara-python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

Ou modifiez le `requirements.txt` :

```txt
# Décommenter cette ligne
yara-python>=4.3.0
```

Puis rebuilder l'image :

```bash
docker-compose build --no-cache
```

---

## 🧪 Test de l'installation

### Script de test rapide

```python
# test_yara.py
import yara

# Règle simple
rule = """
rule test_rule {
    strings:
        $hello = "hello"
    condition:
        $hello
}
"""

# Compiler la règle
rules = yara.compile(source=rule)

# Tester sur du texte
matches = rules.match(data=b"hello world")

if matches:
    print("✅ YARA fonctionne correctement !")
    print(f"   Règle détectée: {matches[0].rule}")
else:
    print("❌ Aucune détection (mais YARA fonctionne)")
```

Exécuter :

```bash
python test_yara.py
```

### Test avec DNA-Sec

```bash
# Tester avec une séquence malveillante
dna-sec examples/shellcode/shellcode.fasta

# Devrait afficher "risk_score: 90" si YARA fonctionne
```

---

## 🔧 Dépannage

### Erreur : Module not found

```python
ImportError: No module named 'yara'
```

**Solution** : YARA n'est pas installé
```bash
pip install yara-python
```

---

### Erreur : DLL load failed (Windows)

```python
ImportError: DLL load failed while importing yara
```

**Solutions** :
1. Installer Visual C++ Redistributable
2. Utiliser une wheel précompilée
3. Passer en mode DEMO (sans YARA)

---

### Erreur : libyara.so not found (Linux)

```python
OSError: libyara.so.9: cannot open shared object file
```

**Solution** :
```bash
sudo ldconfig
# ou
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

---

### Erreur : Version mismatch

```python
RuntimeError: YARA version mismatch
```

**Solution** : Réinstaller en version cohérente
```bash
pip uninstall yara-python
# Puis réinstaller avec la méthode appropriée
```

---

## 🚀 Mode sans YARA (Fallback)

Si l'installation de YARA échoue, DNA-Sec fonctionne quand même :

### Avantages du mode Fallback

✅ Pas de dépendances complexes  
✅ Fonctionne sur tous les OS  
✅ Installation rapide  
✅ Détection basique fonctionnelle

### Limitations

⚠️ Détection moins précise  
⚠️ Patterns limités  
⚠️ Pas de règles YARA custom

### Utilisation

```bash
# CLI - Détecte automatiquement si YARA est absent
dna-sec examples/malicious_dna.fasta

# Web - Mode DEMO
cd web
python app_demo.py
```

---

## 📚 Ressources

- [YARA Documentation officielle](https://yara.readthedocs.io/)
- [YARA GitHub](https://github.com/VirusTotal/yara)
- [yara-python GitHub](https://github.com/VirusTotal/yara-python)
- [VirusTotal YARA Rules](https://github.com/Yara-Rules/rules)
- [Awesome YARA](https://github.com/InQuest/awesome-yara)

---

## ✉️ Support

Si vous rencontrez des problèmes :

1. Vérifier les [Issues GitHub](https://github.com/VirusTotal/yara-python/issues)
2. Consulter la [documentation YARA](https://yara.readthedocs.io/)
3. Utiliser le mode DEMO en attendant
4. Ouvrir une issue sur le projet DNA-Sec

**En cas de blocage** : Le mode sans YARA est tout à fait utilisable pour la plupart des cas d'usage ! 🚀
