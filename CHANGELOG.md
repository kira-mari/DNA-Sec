# Changelog

All notable changes to DNA-Sec will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for RNA sequences (U instead of T)
- PDF export for scan reports
- GraphQL API
- Machine learning anomaly detection
- PostgreSQL database support
- User authentication system

---

## [0.1.0] - 2025-10-28

### Added - Project Organization

#### Testing Infrastructure
- ✅ Restructured tests into `unit/` and `integration/` directories
- ✅ Added `conftest.py` with shared pytest fixtures
- ✅ Added `pytest.ini` with test configuration and markers
- ✅ Created `__init__.py` files for test packages
- ✅ Added 13 comprehensive unit tests
  - `test_parser.py` (4 tests)
  - `test_scanner.py` (5 tests)  
  - `test_cli.py` (4 tests)
  - `test_decoder.py` (existing)

#### Documentation
- ✅ Created `docs/` directory for technical documentation
- ✅ Added `docs/ARCHITECTURE.md` - Complete architecture documentation
- ✅ Added `docs/INSTALL_YARA.md` - Detailed YARA installation guide
- ✅ Consolidated all README files into single `README.md`
- ✅ Removed 13 redundant README files

#### Development Tools
- ✅ Added `tasks.ps1` - PowerShell task runner for Windows
  - 12 common development tasks
  - install, test, coverage, web, clean, lint, format, docker, etc.
- ✅ Added `Makefile` - Make commands for Linux/macOS
  - Cross-platform development commands
- ✅ Added `.editorconfig` - Editor configuration standards
- ✅ Added `start_web.sh` - Bash startup script for Linux/macOS
- ✅ Improved `start_web.ps1` - Enhanced PowerShell startup script

#### CI/CD
- ✅ Added `.github/workflows/tests.yml` - GitHub Actions pipeline
  - Multi-OS testing (Ubuntu, Windows, macOS)
  - Multi-Python version (3.8, 3.9, 3.10, 3.11)
  - Automated linting and formatting checks
  - Docker build testing
  - Code coverage reporting

#### Configuration
- ✅ Unified `requirements.txt` (removed `requirements-full.txt`)
- ✅ Updated `.gitignore` to exclude `.env` (only `.env.example` tracked)

### Added - Core Features

#### YARA Optional Support
- ✅ Made YARA completely optional with graceful fallback
- ✅ Added `_mock_scan()` function for basic pattern detection
- ✅ Scanner works without YARA installation
- ✅ Automatic detection and fallback to mock scanner

#### Security Enhancements
- ✅ Rate limiting (10 requests/minute per IP) on web API
- ✅ In-memory rate limit tracking with datetime
- ✅ File size limits (10MB max)
- ✅ Scan timeout (30 seconds)
- ✅ Auto-cleanup of temporary files (5 minutes)
- ✅ No persistent storage (ephemeral uploads)

#### Docker Support
- ✅ Production-ready `Dockerfile`
  - Python 3.11-slim base image
  - Non-root user (dna-sec, uid 1000)
  - Health check on `/api/health`
  - Security hardened
- ✅ `docker-compose.yml` with full orchestration
  - Volume mounts for examples and uploads
  - Environment variables support
  - Optional nginx reverse proxy (production profile)
  - Resource limits (CPU, memory)

#### Documentation & Licensing
- ✅ Added `LICENSE` file (MIT License)
- ✅ Added `CONTRIBUTING.md` - Comprehensive contribution guide
- ✅ Added `.env.example` - Configuration template
- ✅ Updated `README.md` with complete documentation

### Changed

#### File Organization
- 📁 Moved tests to structured directories:
  - `tests/` → `tests/unit/` and `tests/integration/`
- 📁 Consolidated documentation:
  - Removed: `README_COMPLET.md`, `QUICKSTART.md`, `PROJECT_REVIEW.md`
  - Removed: `web/README.md`, `web/INSTALL_YARA.md`, `web/ARCHITECTURE.md`
  - Removed: 7 example subdirectory README files
- 📁 Created `docs/` for technical documentation

#### Dependencies
- 📦 Simplified to single `requirements.txt`
- 📦 Added pytest and pytest-cov to requirements
- 📦 YARA remains optional (commented with instructions)

### Fixed
- 🐛 Fixed duplicate `get_shellcode_explanation()` function in `scanner.py`
- 🐛 Removed obsolete `report.json` file
- 🐛 Cleaned up all `__pycache__` directories
- 🐛 Improved error handling for missing YARA

### Security
- 🔒 Environment variables now in `.env.example` (template only)
- 🔒 `.env` added to `.gitignore` (secrets not committed)
- 🔒 Docker container runs as non-root user
- 🔒 Rate limiting prevents API abuse

---

## [0.0.1] - Initial Release

### Added
- Initial DNA sequence malware scanner
- FASTA and GenBank file support
- DNA to binary decoder (A=00, C=01, G=10, T=11)
- YARA rule-based detection
- CLI interface with Click
- Web interface with Flask
- Example malicious sequences
- Basic unit tests

---

## Legend

- ✅ Completed
- 📁 File organization
- 📦 Dependencies
- 🐛 Bug fix
- 🔒 Security
- 🎨 UI/Design
- 📚 Documentation
- 🚀 Performance
- ⚠️ Deprecated

---

## Release Notes

### Version 0.1.0 Highlights

This release focuses on **project organization, testing infrastructure, and production readiness**:

🎯 **Key Improvements:**
1. **Professional Testing** - Restructured tests with pytest best practices
2. **Better Documentation** - Consolidated and organized all docs
3. **Developer Experience** - Task runners, Makefile, CI/CD pipeline
4. **Production Ready** - Docker, security hardening, rate limiting
5. **Optional YARA** - Works without YARA installation

📊 **Statistics:**
- 11 new configuration files
- 13 comprehensive unit tests
- 2 detailed documentation guides
- 13 redundant files removed
- 100% backward compatible

🚀 **Next Steps:**
See [Unreleased] section for planned features in v0.2.0

---

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
