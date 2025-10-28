# DNA-Sec - Gestionnaire de tâches PowerShell
# Collection de tâches de développement courantes

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

function Show-Help {
    Write-Host ""
    Write-Host "DNA-Sec - Tâches disponibles" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\tasks.ps1 <tache>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Taches disponibles:" -ForegroundColor White
    Write-Host ""
    Write-Host "  install       " -ForegroundColor Green -NoNewline
    Write-Host "  Installer toutes les dependances"
    Write-Host "  test          " -ForegroundColor Green -NoNewline
    Write-Host "  Lancer tous les tests"
    Write-Host "  test-unit     " -ForegroundColor Green -NoNewline
    Write-Host "  Lancer les tests unitaires uniquement"
    Write-Host "  test-integration" -ForegroundColor Green -NoNewline
    Write-Host " Lancer les tests d'integration uniquement"
    Write-Host "  coverage      " -ForegroundColor Green -NoNewline
    Write-Host "  Lancer les tests avec rapport de couverture"
    Write-Host "  web           " -ForegroundColor Green -NoNewline
    Write-Host "  Demarrer l'interface web (mode DEMO)"
    Write-Host "  web-full      " -ForegroundColor Green -NoNewline
    Write-Host "  Demarrer l'interface web (avec YARA)"
    Write-Host "  clean         " -ForegroundColor Green -NoNewline
    Write-Host "  Nettoyer les fichiers temporaires et caches"
    Write-Host "  lint          " -ForegroundColor Green -NoNewline
    Write-Host "  Verifier le style du code (necessite flake8)"
    Write-Host "  format        " -ForegroundColor Green -NoNewline
    Write-Host "  Formater le code (necessite black)"
    Write-Host "  docker-build  " -ForegroundColor Green -NoNewline
    Write-Host "  Construire l'image Docker"
    Write-Host "  docker-run    " -ForegroundColor Green -NoNewline
    Write-Host "  Lancer le conteneur Docker"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install -e .
    Write-Host "[OK] Dependances installees" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "Lancement de tous les tests..." -ForegroundColor Yellow
    pytest tests/ -v
}

function Run-UnitTests {
    Write-Host "Lancement des tests unitaires..." -ForegroundColor Yellow
    pytest tests/unit/ -v -m unit
}

function Run-IntegrationTests {
    Write-Host "Lancement des tests d'integration..." -ForegroundColor Yellow
    pytest tests/integration/ -v -m integration
}

function Run-Coverage {
    Write-Host "Lancement des tests avec couverture..." -ForegroundColor Yellow
    pytest tests/ --cov=dna_sec --cov-report=html --cov-report=term
    Write-Host ""
    Write-Host "[OK] Rapport de couverture genere dans htmlcov/index.html" -ForegroundColor Green
}

function Start-Web {
    Write-Host "Demarrage de l'interface web (mode DEMO)..." -ForegroundColor Yellow
    Set-Location web
    python app_demo.py
}

function Start-WebFull {
    Write-Host "Demarrage de l'interface web (mode COMPLET)..." -ForegroundColor Yellow
    Set-Location web
    python app.py
}

function Clean-Project {
    Write-Host "Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
    
    # Cache Python
    Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Include *.pyc -Recurse -File | Remove-Item -Force
    Get-ChildItem -Path . -Include *.pyo -Recurse -File | Remove-Item -Force
    
    # Cache de tests
    if (Test-Path .pytest_cache) { Remove-Item .pytest_cache -Recurse -Force }
    if (Test-Path htmlcov) { Remove-Item htmlcov -Recurse -Force }
    if (Test-Path .coverage) { Remove-Item .coverage -Force }
    
    # Artefacts de build
    if (Test-Path build) { Remove-Item build -Recurse -Force }
    if (Test-Path dist) { Remove-Item dist -Recurse -Force }
    Get-ChildItem -Path . -Include *.egg-info -Recurse -Directory | Remove-Item -Recurse -Force
    
    # Uploads temporaires
    if (Test-Path web/uploads) {
        Get-ChildItem web/uploads -File | Remove-Item -Force
    }
    
    Write-Host "[OK] Nettoyage termine" -ForegroundColor Green
}

function Run-Lint {
    Write-Host "Verification du style du code..." -ForegroundColor Yellow
    $output = flake8 dna_sec/ tests/ --max-line-length=100 2>&1
    
    if ($LASTEXITCODE -eq 0 -and [string]::IsNullOrWhiteSpace($output)) {
        Write-Host "[OK] Aucune erreur de style trouvee! Le code est propre." -ForegroundColor Green
    } else {
        Write-Host $output
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERREUR] Erreurs de style trouvees. Veuillez les corriger." -ForegroundColor Red
        }
    }
}

function Run-Format {
    Write-Host "Formatage du code..." -ForegroundColor Yellow
    black dna_sec/ tests/ --line-length=100
    Write-Host "[OK] Code formate" -ForegroundColor Green
}

function Build-Docker {
    Write-Host "Construction de l'image Docker..." -ForegroundColor Yellow
    docker-compose build
    Write-Host "[OK] Image Docker construite" -ForegroundColor Green
}

function Run-Docker {
    Write-Host "Demarrage du conteneur Docker..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "[OK] Conteneur demarre sur http://localhost:5000" -ForegroundColor Green
}

# Executer la tache
switch ($Task.ToLower()) {
    "install" { Install-Dependencies }
    "test" { Run-Tests }
    "test-unit" { Run-UnitTests }
    "test-integration" { Run-IntegrationTests }
    "coverage" { Run-Coverage }
    "web" { Start-Web }
    "web-full" { Start-WebFull }
    "clean" { Clean-Project }
    "lint" { Run-Lint }
    "format" { Run-Format }
    "docker-build" { Build-Docker }
    "docker-run" { Run-Docker }
    "help" { Show-Help }
    default {
        Write-Host "[ERREUR] Tache inconnue: $Task" -ForegroundColor Red
        Show-Help
    }
}
