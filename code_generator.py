import os
from model.uml_model import UMLClass, UMLAttribute, UMLMethod, UMLMultiplicity

class JavaCodeGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    # Génération des fichiers Java pour chaque classe UML
    def generate(self, classes: list[UMLClass]):
        for uml_class in classes:
            self._generate_class_file(uml_class)

    def _generate_class_file(self, uml_class: UMLClass):
        file_path = os.path.join(self.output_dir, f"{uml_class.name}.java")

        with open(file_path, 'w') as file:
            file.write(self._generate_class_code(uml_class))

    def _generate_class_code(self, uml_class: UMLClass) -> str:
        lines = []

        # Ajout du package
        lines.append("//package com.example.myproject;")
        lines.append("")

        # Ajout des imports
        lines.append("//import java.util.*;")
        lines.append("")

        # Déclaration de la classe
        lines.append(self._generate_class_declaration(uml_class))
        lines.append("{")

        # Attributs avec commentaires
        for attr in uml_class.attributes:
            lines.append(f"    private {attr.type} {attr.name};")
        lines.append("")

        # Constructeur par défaut
        lines.append(f"    public {uml_class.name}() {{")
        lines.append("    }")
        lines.append("")

        # Getters et Setters
        for attr in uml_class.attributes:
            lines.append(self._generate_getter(attr))
            lines.append("")
            lines.append(self._generate_setter(attr))
            lines.append("")

        # Méthodes
        for method in uml_class.methods:
            lines.append(self._generate_method(method))
            lines.append("")

        # Relations (si définies)
        for relation in uml_class.relations:
            lines.append(f"    // Relation: {relation.type} with {relation.target_id}")
        lines.append("")

        # Fin de la classe
        lines.append("}")

        return "\n".join(lines)

    def _generate_class_declaration(self, uml_class: UMLClass) -> str:
        
        #Génère la déclaration de la classe
        parts = ["public"]

        # Gestion des stéréotypes
        if "abstract" in uml_class.stereotypes:
            parts.append("abstract")
        if "interface" in uml_class.stereotypes:
            parts = ["public", "interface"]
        if uml_class.is_abstract:
            parts.append("abstract")

        parts.append("class" if "interface" not in parts else "interface")
        parts.append(uml_class.name)

        # Gestion des génériques
        if uml_class.generics:
            parts[-1] += f"<{', '.join(uml_class.generics)}>"


        if uml_class.superclasses and "interface" not in parts:
            parts.append("extends " + ", ".join(uml_class.superclasses))

        if uml_class.interfaces:
            parts.append("implements " + ", ".join(uml_class.interfaces))

        return " ".join(parts)

    def _generate_getter(self, attr) -> str:
        
        #Génère le getter pour un attribut
        return f"""    public {attr.type} get{attr.name.capitalize()}() {{
        return {attr.name};
    }}"""

    def _generate_setter(self, attr) -> str:
    
        #Génère le setter pour un attribut        
        return f"""    public void set{attr.name.capitalize()}({attr.type} {attr.name}) {{
        this.{attr.name} = {attr.name};
    }}"""

    def _generate_method(self, method: UMLMethod) -> str:
        # Gestion des modificateurs
        modifiers = [method.visibility]
        if method.is_static:
            modifiers.append("static")
        if method.is_final:
            modifiers.append("final")
        if method.is_abstract:
            modifiers.append("abstract")

        # Gestion des génériques dans les méthodes
        method_generics = [f"{p[0]}:{p[1]}" for p in method.parameters if p[2].max != 1]
        generic_str = f"<{', '.join(method_generics)}>" if method_generics else ""

        #Génère le code pour une méthode
        params = [
            f"{self._get_java_type(param_type, mult)} {param_name}" 
            for param_name, param_type, mult in method.parameters
        ]

        # Gestion des exceptions
        throws_str = f" throws {', '.join(method.throws)}" if method.throws else ""

        # Ajouter un return par défaut si nécessaire
        default_return = ""
        if method.return_type != "void":
            if method.return_type in ["int", "long", "short", "byte"]:
                default_return = "        return 0;"
            elif method.return_type in ["float", "double"]:
                default_return = "        return 0.0;"
            elif method.return_type == "boolean":
                default_return = "        return false;"
            else:
                default_return = "        return null;"

        method_str = f"""    {' '.join(modifiers)} {generic_str} {method.return_type} {method.name}({', '.join(params)}){throws_str} {{
            // Méthode générée automatiquement
    {default_return}
        }}"""
        return method_str

def _generate_attribute(self, attr: UMLAttribute) -> str:
        # Gestion des attributs dérivés et avec multiplicité
        modifiers = []
        if attr.is_static:
            modifiers.append("static")
        if attr.is_final:
            modifiers.append("final")
        
        type_ = self._get_java_type(attr.type, attr.multiplicity)
        prefix = "/" if attr.is_derived else ""

        return f"    {attr.visibility} {' '.join(modifiers)} {type_} {prefix}{attr.name};"