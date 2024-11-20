from flask import Flask, request, send_file
from flask_cors import CORS


import os
import tempfile
import zipfile
import subprocess
app = Flask(__name__)
CORS(app)
@app.route('/generate-java-classes', methods=['POST'])
def generate_java_classes():
    # Vérifier si un fichier est présent
    if 'drawioFile' not in request.files:
        return 'Aucun fichier', 400

    file = request.files['drawioFile']
    
    # Créer des répertoires temporaires
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        # Sauvegarder le fichier DrawIO
        input_path = os.path.join(input_dir, file.filename)
        file.save(input_path)

        # Exécuter le script Python
        subprocess.run([
            'python3', 
            'main.py', 
            input_path, 
            output_dir
        ], check=True)

        # Créer un ZIP des classes générées
        zip_path = os.path.join(input_dir, 'java_classes.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    zipf.write(
                        os.path.join(root, file), 
                        arcname=file
                    )

        # Retourner le fichier ZIP
        return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
