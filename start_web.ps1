# 🧬 DNA-Sec - Démarrage rapide (PowerShell)
# Script pour lancer facilement l'interface web

Write-Host "🧬 DNA-Sec - Démarrage de l'interface web" -ForegroundColor Cyan
Write-Host ""

# Vérifier si dans le bon dossier
if (-not (Test-Path "web/app_demo.py")) {
    Write-Host "❌ Erreur: Exécutez ce script depuis le dossier racine DNA/" -ForegroundColor Red
    exit 1
}

# Vérifier Python
Write-Host "🔍 Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Installer les dépendances si nécessaire
Write-Host ""
Write-Host "📦 Vérification des dépendances..." -ForegroundColor Yellow

$flaskInstalled = python -c "import flask" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚙️  Installation de Flask..." -ForegroundColor Yellow
    pip install flask werkzeug
}

$biopythonInstalled = python -c "import Bio" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚙️  Installation des dépendances..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "✅ Dépendances OK" -ForegroundColor Green

# Choisir le mode
Write-Host ""
Write-Host "🚀 Choisissez le mode de démarrage:" -ForegroundColor Cyan
Write-Host "  1. Mode DEMO (sans YARA) - Recommandé pour tester" -ForegroundColor White
Write-Host "  2. Mode COMPLET (avec YARA) - Nécessite YARA installé" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Votre choix (1 ou 2)"

if ($choice -eq "2") {
    # Vérifier si YARA est installé
    $yaraInstalled = python -c "import yara" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "⚠️  YARA n'est pas installé ou mal configuré" -ForegroundColor Yellow
        Write-Host "   Consultez web/INSTALL_YARA.md pour l'installation" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Basculement sur le mode DEMO..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        $appFile = "app_demo.py"
    } else {
        $appFile = "app.py"
    }
} else {
    $appFile = "app_demo.py"
}

# Lancer le serveur
Write-Host ""
Write-Host "🌐 Démarrage du serveur web..." -ForegroundColor Cyan
Write-Host "   URL: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

Set-Location web
python $appFile
