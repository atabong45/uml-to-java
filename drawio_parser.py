import xml.etree.ElementTree as ET
from model.uml_model import UMLClass, UMLAttribute, UMLMethod, UMLRelation, UMLMultiplicity
import re

class DrawIOParser:
    def __init__(self):
        self.namespace = {'xmlns': 'http://www.w3.org/1999/xhtml'}

    def _parse_multiplicity(self, mult_str: str) -> UMLMultiplicity:
            if not mult_str or mult_str == '*':
                return UMLMultiplicity(min=0, max=None)
            
            if '..' in mult_str:
                min_val, max_val = mult_str.split('..')
                return UMLMultiplicity(
                    min=int(min_val), 
                    max=None if max_val == '*' else int(max_val)
                )
            
            return UMLMultiplicity(min=int(mult_str), max=int(mult_str))



    def parse(self, file_path: str) -> list[UMLClass]:
        """
        Parse un fichier .drawio et retourne une liste de classes UML
        """
        tree = ET.parse(file_path)
        root = tree.getroot()

        cells = root.findall(".//mxCell")

        classes = {}
        relations = []

        # Analyse des classes et relations
        for cell in cells:
            if self._is_class(cell):
                uml_class = self._parse_class(cell)
                classes[cell.get('id')] = uml_class


        # Analyse des attributs/méthodes pour chaque classe
        for cell in cells:
            if self._is_attribute_or_method(cell):
                parent_id = cell.get('parent')
                if parent_id in classes:
                    self._process_attribute_or_method(classes[parent_id], cell)

         # Analyse des relations
        for cell in cells:
            if self._is_relation(cell):
                relations.append(self._parse_relation(cell))


        # Ajout des relations (héritage ou autre)
        self._process_relations(relations, classes)

        return list(classes.values())

    def _is_class(self, cell) -> bool:
        style = cell.get('style', '')
        return 'swimlane' in style and cell.get('vertex') == '1'

    def _is_relation(self, cell) -> bool:
        return cell.get('edge') == '1'

    def _is_attribute_or_method(self, cell) -> bool:
        value = cell.get('value', '').strip()
        return value and cell.get('vertex') == '1' and 'swimlane' not in cell.get('style', '')

    def _parse_class(self, cell) -> UMLClass:
        class_name = cell.get('value', '').split('\n')[0].strip()
        return UMLClass(class_name)

    def _process_attribute_or_method(self, uml_class: UMLClass, cell):
        value = cell.get('value', '').strip()

        # verification si la donnee est une methode ou un attribut : pour attribut et () pour la methode
        if '(' in value:
            uml_class.add_method(self._parse_method(value))
        elif ':' in value:
            uml_class.add_attribute(self._parse_attribute(value))


    def _parse_attribute(self, attr_string: str) -> UMLAttribute:
        parts = attr_string.split(':')
        name = parts[0].strip()
        type_ = parts[1].strip() if len(parts) > 1 else "String"

        visibility = "private"
        if name.startswith('+'):
            visibility = "public"
            name = name[1:]
        elif name.startswith('-'):
            visibility = "private"
            name = name[1:]
        elif name.startswith('#'):
            visibility = "protected"
            name = name[1:]

        # Gérer les attributs dérivés
        is_derived = name.startswith('/')
        if is_derived:
            name = name.lstrip('/')
         # Gestion de la multiplicité (avec regex)
        multiplicity = UMLMultiplicity()
        mult_match = re.search(r'\[(\d+\.?\d*)\]', type_)
        if mult_match:
            multiplicity = self._parse_multiplicity(mult_match.group(1))
            type_ = type_.replace(mult_match.group(0), '').strip()
    
        return UMLAttribute(
        name=name, 
        type=type_, 
        visibility=visibility,
        is_derived=is_derived,
        multiplicity=multiplicity
    )

    def _parse_method(self, method_string: str) -> UMLMethod:

        parts = method_string.split('(')
        name = parts[0].strip()

        # Déterminer la visibilité des donnees
        visibility = "public"
        if name.startswith('+'):
            visibility = "public"
            name = name[1:]
        elif name.startswith('-'):
            visibility = "private"
            name = name[1:]
        elif name.startswith('#'):
            visibility = "protected"
            name = name[1:]

        # definition des Paramètres et type de retour
        return_type = "void"
        parameters = []
        throws = []
        is_abstract = False
        is_static = False
        is_final = False

        # Gestion des modificateurs
        if "abstract" in method_string:
            is_abstract = True
        if "static" in method_string:
            is_static = True
        if "final" in method_string:
            is_final = True

        # Gestion des exceptions
        throws_match = re.search(r'throws\s+(\w+(?:,\s*\w+)*)', method_string)
        if throws_match:
            throws = [e.strip() for e in throws_match.group(1).split(',')]

        # Analyse des paramètres
        if len(parts) > 1:
            param_section = parts[1].split(')')[0]
            if param_section:
                param_pairs = param_section.split(',')
                for param in param_pairs:
                    param_parts = param.strip().split(':')
                    if len(param_parts) == 2:
                        param_name, param_type = param_parts
                        # Gestion de la multiplicité
                        mult_match = re.search(r'\[(\d+\.?\d*)\]', param_type)
                        multiplicity = self._parse_multiplicity(mult_match.group(1)) if mult_match else UMLMultiplicity()
                        param_type = param_type.replace(mult_match.group(0), '').strip() if mult_match else param_type
                        
                        parameters.append((
                            param_name.strip(), 
                            param_type.strip(), 
                            multiplicity
                        ))
            if ':' in parts[1]:
                return_type = parts[1].split(':')[1].strip().split(')')[0]

        return UMLMethod(
            name=name, 
            return_type=return_type, 
            parameters=parameters, 
            visibility=visibility,
            throws=throws,
            is_abstract=is_abstract,
            is_static=is_static,
            is_final=is_final
        )

    def _process_class_additional_details(self, uml_class: UMLClass, cell):
        
        #Extraction des détails supplémentaires de la classe
        value = cell.get('value', '')

        # Extraction du stéréotype
        stereo_match = re.search(r'<<(\w+)>>', value)
        if stereo_match:
            uml_class.stereotypes.append(stereo_match.group(1))
        
        # Marquer comme interface ou abstract si stéréotype
        if 'interface' in uml_class.stereotypes:
            uml_class.is_interface = True
        # Extraction des génériques
        generics_match = re.search(r'<(\w+(?:,\s*\w+)*)>', value)
        if generics_match:
            uml_class.generics = [g.strip() for g in generics_match.group(1).split(',')]


    def _parse_relation(self, cell) -> UMLRelation:
        source_id = cell.get('source')
        target_id = cell.get('target')
        style = cell.get('style', '')

        relation_type = self._determine_relation_type(style)

        return UMLRelation(source_id, target_id, relation_type)

    def _determine_relation_type(self, style: str) -> str:
        if 'endArrow=diamond' in style:
            return "composition"
        elif 'endArrow=diamondThin' in style:
            return "aggregation"
        elif 'endArrow=block' in style:
            return "inheritance"
        else:
            return "association"

    def _process_relations(self, relations: list[UMLRelation], classes: dict):
        for relation in relations:
            if relation.source_id in classes and relation.target_id in classes:
                source_class = classes[relation.source_id]
                target_class = classes[relation.target_id]

                if relation.type == "inheritance":
                    source_class.add_superclass(target_class.name)
                else:
                    source_class.add_relation(relation.type, target_class.name)
