# Makefile pour DNA-Sec
# Commandes multi-plateformes pour tâches courantes

.PHONY: help install test test-unit test-integration coverage web clean lint format docker-build docker-run

help:
	@echo "DNA-Sec - Commandes disponibles"
	@echo "================================"
	@echo ""
	@echo "  make install          Installer toutes les dependances"
	@echo "  make test             Lancer tous les tests"
	@echo "  make test-unit        Lancer les tests unitaires uniquement"
	@echo "  make test-integration Lancer les tests d'integration uniquement"
	@echo "  make coverage         Lancer les tests avec rapport de couverture"
	@echo "  make web              Demarrer l'interface web (mode DEMO)"
	@echo "  make web-full         Demarrer l'interface web (avec YARA)"
	@echo "  make clean            Nettoyer les fichiers temporaires et caches"
	@echo "  make lint             Verifier le style du code"
	@echo "  make format           Formater le code avec black"
	@echo "  make docker-build     Construire l'image Docker"
	@echo "  make docker-run       Lancer le conteneur Docker"
	@echo ""

install:
	@echo "Installation des dependances..."
	pip install -r requirements.txt
	pip install -e .
	@echo "[OK] Dependances installees"

test:
	@echo "Lancement de tous les tests..."
	pytest tests/ -v

test-unit:
	@echo "Lancement des tests unitaires..."
	pytest tests/unit/ -v -m unit

test-integration:
	@echo "Lancement des tests d'integration..."
	pytest tests/integration/ -v -m integration

coverage:
	@echo "Lancement des tests avec couverture..."
	pytest tests/ --cov=dna_sec --cov-report=html --cov-report=term
	@echo ""
	@echo "[OK] Rapport de couverture genere dans htmlcov/index.html"

web:
	@echo "Demarrage de l'interface web (mode DEMO)..."
	cd web && python app_demo.py

web-full:
	@echo "Demarrage de l'interface web (mode COMPLET)..."
	cd web && python app.py

clean:
	@echo "Nettoyage des fichiers temporaires..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf build dist *.egg-info
	rm -f web/uploads/* 2>/dev/null || true
	@echo "[OK] Nettoyage termine"

lint:
	@echo "Verification du style du code..."
	flake8 dna_sec/ tests/ --max-line-length=100

format:
	@echo "Formatage du code..."
	black dna_sec/ tests/ --line-length=100
	@echo "[OK] Code formate"

docker-build:
	@echo "Construction de l'image Docker..."
	docker-compose build
	@echo "[OK] Image Docker construite"

docker-run:
	@echo "Demarrage du conteneur Docker..."
	docker-compose up -d
	@echo "[OK] Conteneur demarre sur http://localhost:5000"
