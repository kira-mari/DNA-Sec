"""
DNA-Sec Web Interface
Interface web sécurisée pour l'analyse de séquences ADN
"""
import os
import sys
import tempfile
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import atexit
import threading

# Ajouter le dossier parent au path pour importer dna_sec
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_sec.parser import load_dna_sequence
from dna_sec.scanner import scan_dna_for_malware

app = Flask(__name__)

# Configuration sécurisée
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'fasta', 'fa', 'fna', 'gb', 'gbk', 'genbank'}
app.config['SCAN_TIMEOUT'] = 30  # secondes

# Rate limiting en mémoire
rate_limit_data = defaultdict(list)
rate_limit_lock = threading.Lock()
RATE_LIMIT_REQUESTS = 10  # requêtes par minute
RATE_LIMIT_WINDOW = 60  # secondes

# Dictionnaire en mémoire pour les fichiers temporaires (auto-cleanup)
temp_files = {}
cleanup_lock = threading.Lock()

def check_rate_limit(ip_address):
    """Vérifie si l'IP a dépassé la limite de requêtes"""
    with rate_limit_lock:
        now = datetime.now()
        # Nettoyer les anciennes requêtes
        rate_limit_data[ip_address] = [
            timestamp for timestamp in rate_limit_data[ip_address]
            if now - timestamp < timedelta(seconds=RATE_LIMIT_WINDOW)
        ]
        
        # Vérifier la limite
        if len(rate_limit_data[ip_address]) >= RATE_LIMIT_REQUESTS:
            return False, len(rate_limit_data[ip_address])
        
        # Enregistrer la nouvelle requête
        rate_limit_data[ip_address].append(now)
        return True, len(rate_limit_data[ip_address])

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_old_files():
    """Nettoie les fichiers temporaires de plus de 5 minutes"""
    with cleanup_lock:
        current_time = time.time()
        to_delete = []
        for file_id, (filepath, timestamp) in temp_files.items():
            if current_time - timestamp > 300:  # 5 minutes
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    to_delete.append(file_id)
                except Exception:
                    pass
        for file_id in to_delete:
            del temp_files[file_id]

def cleanup_all_files():
    """Nettoie tous les fichiers temporaires au shutdown"""
    with cleanup_lock:
        for file_id, (filepath, _) in temp_files.items():
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass
        temp_files.clear()

# Enregistrer le cleanup au shutdown
atexit.register(cleanup_all_files)

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    """
    API d'analyse de fichier ADN
    Sécurisé : validation, timeout, cleanup auto, rate limiting
    """
    # Rate limiting
    ip_address = request.remote_addr
    allowed, request_count = check_rate_limit(ip_address)
    
    if not allowed:
        return jsonify({
            'error': f'Limite de requêtes dépassée ({RATE_LIMIT_REQUESTS}/min). Réessayez plus tard.',
            'retry_after': 60
        }), 429
    
    cleanup_old_files()
    
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Format non supporté. Utilisez: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
        }), 400
    
    # Créer un fichier temporaire sécurisé
    try:
        # Utiliser tempfile pour éviter les collisions
        fd, temp_path = tempfile.mkstemp(
            suffix=f".{file.filename.rsplit('.', 1)[1].lower()}",
            dir=app.config['UPLOAD_FOLDER']
        )
        os.close(fd)
        
        # Sauvegarder le fichier
        file.save(temp_path)
        
        # Stocker dans le dict en mémoire avec timestamp
        file_id = os.path.basename(temp_path)
        with cleanup_lock:
            temp_files[file_id] = (temp_path, time.time())
        
        # Analyser avec timeout
        start_time = time.time()
        
        # Parser la séquence
        dna_seq = load_dna_sequence(temp_path)
        
        # Vérifier timeout
        if time.time() - start_time > app.config['SCAN_TIMEOUT']:
            raise TimeoutError("Analyse trop longue")
        
        # Scanner pour malware
        report = scan_dna_for_malware(dna_seq)
        
        # Vérifier timeout final
        if time.time() - start_time > app.config['SCAN_TIMEOUT']:
            raise TimeoutError("Analyse trop longue")
        
        # Ajouter métadonnées
        report['filename'] = secure_filename(file.filename)
        report['sequence_length'] = len(dna_seq)
        report['scan_time'] = round(time.time() - start_time, 3)
        
        # Nettoyer immédiatement le fichier
        try:
            os.remove(temp_path)
            with cleanup_lock:
                if file_id in temp_files:
                    del temp_files[file_id]
        except Exception:
            pass
        
        return jsonify(report), 200
        
    except ValueError as e:
        # Erreur de parsing (bases invalides, format incorrect, etc.)
        return jsonify({'error': f'Erreur de parsing: {str(e)}'}), 400
    
    except TimeoutError as e:
        return jsonify({'error': str(e)}), 408
    
    except Exception as e:
        # Erreur générique
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    
    finally:
        # Cleanup de sécurité
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
                with cleanup_lock:
                    if 'file_id' in locals() and file_id in temp_files:
                        del temp_files[file_id]
        except Exception:
            pass

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de santé pour monitoring"""
    return jsonify({
        'status': 'ok',
        'temp_files_count': len(temp_files)
    }), 200

if __name__ == '__main__':
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Lancer le serveur en mode développement
    print("DNA-Sec Interface Web")
    print("Serveur demarre sur http://localhost:5000")
    print("Securite: timeout 30s, max 10MB, auto-cleanup 5min")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
