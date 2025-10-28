"""
DNA-Sec Web Interface (Demo Mode - Sans YARA)
Pour développer et tester le frontend sans dépendre de YARA
"""
import os
import sys
import tempfile
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import atexit
import threading

# Ajouter le dossier parent au path pour importer dna_sec
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna_sec.parser import load_dna_sequence

app = Flask(__name__)

# Configuration sécurisée
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'fasta', 'fa', 'fna', 'gb', 'gbk', 'genbank'}
app.config['SCAN_TIMEOUT'] = 30  # secondes

# Dictionnaire en mémoire pour les fichiers temporaires (auto-cleanup)
temp_files = {}
cleanup_lock = threading.Lock()

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

def mock_scan_dna_for_malware(dna_seq: str) -> dict:
    """
    Version DEMO du scanner (sans YARA)
    Génère un rapport de démonstration basé sur la longueur de la séquence
    """
    # Simuler une analyse
    time.sleep(1)  # Petit délai pour montrer l'animation
    
    # Déterminer le risk score basé sur des patterns simples
    risk_score = 0
    findings = []
    
    # Pattern 1: Séquences répétitives suspectes
    if 'ATGATGATGATG' in dna_seq:
        risk_score = max(risk_score, 70)
        idx = dna_seq.find('ATGATGATGATG')
        findings.append({
            "frame": 0,
            "offset": idx,
            "rule": "executable_strings_demo",
            "matched_hex": "41544741544741544741",  # Exemple hex
            "matched_ascii": "ATGATGATG",
            "dna_snippet": dna_seq[idx:idx+20],
            "matched_bytes": 12,
            "severity": "high",
            "explanation": "Séquence répétitive détectée (souvent utilisée dans l'encodage de commandes)",
            "impact": "Peut cacher des instructions système répétées",
            "technical_detail": "Pattern répétitif: ATGATGATGATG → Potentielle séquence de démarrage (START codon répété)"
        })
    
    # Pattern 2: Séquence très longue (potentiellement encodage binaire)
    if len(dna_seq) > 5000:
        risk_score = max(risk_score, 50)
        findings.append({
            "frame": 1,
            "offset": 0,
            "rule": "binary_headers_demo",
            "matched_hex": "4D5A9000",  # MZ header simulé
            "matched_ascii": None,
            "dna_snippet": dna_seq[0:20],
            "matched_bytes": 4,
            "severity": "high",
            "explanation": "Séquence longue détectée (>5000 bp) suggérant un encodage de fichier binaire",
            "impact": "Peut contenir un exécutable Windows (PE) ou Linux (ELF) complet",
            "technical_detail": "Signature MZ (4D5A) → Header d'exécutable Windows PE/DOS"
        })
    
    # Pattern 3: Ratio GC anormal (typique d'encodage artificiel)
    gc_count = dna_seq.count('G') + dna_seq.count('C')
    gc_ratio = gc_count / len(dna_seq) if len(dna_seq) > 0 else 0
    
    if gc_ratio < 0.3 or gc_ratio > 0.7:
        risk_score = max(risk_score, 60)
        findings.append({
            "frame": 2,
            "offset": 0,
            "rule": "unusual_gc_content",
            "matched_hex": None,
            "matched_ascii": None,
            "dna_snippet": dna_seq[0:20],
            "matched_bytes": len(dna_seq),
            "severity": "medium",
            "explanation": f"Ratio GC anormal ({gc_ratio*100:.1f}%) - typique d'un encodage artificiel",
            "impact": "L'ADN naturel a généralement un ratio GC entre 30-70%. Un ratio extrême suggère des données encodées artificiellement",
            "technical_detail": f"GC% = {gc_ratio*100:.1f}% (normal: 40-60%) → Suggère encodage non-biologique"
        })
    
    # Pattern 4: Séquences qui ressemblent à du shellcode (pour demo)
    if 'TCCTTTCT' in dna_seq:  # Exemple: encode potentiellement 0x31 0xC0 (xor eax,eax)
        risk_score = max(risk_score, 90)
        idx = dna_seq.find('TCCTTTCT')
        findings.append({
            "frame": 0,
            "offset": idx,
            "rule": "shellcode_x86_common_demo",
            "matched_hex": "31C0",
            "matched_ascii": None,
            "dna_snippet": dna_seq[idx:idx+20],
            "matched_bytes": 2,
            "severity": "critical",
            "explanation": "Opcode shellcode x86 détecté (instruction assembleur)",
            "impact": "Peut exécuter du code machine directement sur le processeur",
            "technical_detail": "Opcode 31C0: xor eax, eax → Met le registre EAX à zéro (technique classique de shellcode)"
        })
    
    return {
        "risk_score": risk_score,
        "findings": findings,
        "recommendation": (
            "Séquence suspecte. Ne pas traiter avec des logiciels non durcis. [DEMO MODE]"
            if risk_score > 50 else
            "Aucune menace détectée. [DEMO MODE]"
        )
    }

# Enregistrer le cleanup au shutdown
atexit.register(cleanup_all_files)

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    """
    API d'analyse de fichier ADN (DEMO MODE)
    Sécurisé : validation, timeout, cleanup auto
    """
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
        
        # Scanner pour malware (MODE DEMO)
        report = mock_scan_dna_for_malware(dna_seq)
        
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
        'mode': 'DEMO (without YARA)',
        'temp_files_count': len(temp_files)
    }), 200

if __name__ == '__main__':
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Lancer le serveur en mode développement
    print("DNA-Sec Interface Web [MODE DEMO - Sans YARA]")
    print("Serveur demarre sur http://localhost:5000")
    print("Securite: timeout 30s, max 10MB, auto-cleanup 5min")
    print("[ATTENTION] DEMO: Utilise un scanner simule sans regles YARA reelles")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
