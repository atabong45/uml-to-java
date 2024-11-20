from drawio_parser import DrawIOParser
from code_generator import JavaCodeGenerator
from model.uml_model import UMLClass, UMLAttribute, UMLMethod, UMLRelation
import os
import sys

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'CODE')

def main(drawio_file_path: str, output_dir: str = None):

    # Utiliser le répertoire par défaut si aucun n'est spécifié
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # Création du répertoire de sortie et ses parents s'ils n'existent pas
    os.makedirs(output_dir, exist_ok=True)

    # Parser le fichier .drawio
    parser = DrawIOParser()
    uml_classes = parser.parse(drawio_file_path)

    # Générer le code Java
    generator = JavaCodeGenerator(output_dir)
    generator.generate(uml_classes)

    print(f"Les fichiers Java ont été générés dans : {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <drawio_file> [output_dir]")
        sys.exit(1)

    drawio_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    main(drawio_file, output_dir)
