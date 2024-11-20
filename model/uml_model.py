from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class UMLMultiplicity:
    min: int = 0
    max: Optional[int] = None  # None représente *
    is_optional: bool = False

@dataclass
class UMLAttribute:
    name: str
    type: str
    visibility: str = "private"
    is_static: bool = False
    is_final: bool = False
    multiplicity: UMLMultiplicity = field(default_factory=UMLMultiplicity)
    is_derived: bool = False  # Pour les attributs dérivés


@dataclass
class UMLMethod:
    name: str
    return_type: str
    parameters: List[Tuple[str, str]] = field(default_factory=list)
    visibility: str = "public"
    is_static: bool = False
    is_abstract: bool = False
    is_final: bool = False
    throws: List[str] = field(default_factory=list)  # Exceptions potentielles


@dataclass
class UMLRelation:
    source_id: str
    target_id: str
    type: str  # "inheritance", "composition", "aggregation", "association"
    source_multiplicity: UMLMultiplicity = field(default_factory=UMLMultiplicity)
    target_multiplicity: UMLMultiplicity = field(default_factory=UMLMultiplicity)
    source_role: str = ""
    target_role: str = ""
    is_navigable: bool = True

@dataclass
class UMLClass:
    name: str
    attributes: List[UMLAttribute] = field(default_factory=list)
    methods: List[UMLMethod] = field(default_factory=list)
    superclasses: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    relations: List[UMLRelation] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False
    package: str = ""
    generics: List[str] = field(default_factory=list)  # Support des génériques
    stereotypes: List[str] = field(default_factory=list)  # Support des stéréotypes


    def add_attribute(self, attribute: UMLAttribute):
        self.attributes.append(attribute)

    def add_method(self, method: UMLMethod):
        self.methods.append(method)

    def add_superclass(self, superclass: str):
        self.superclasses.append(superclass)

    def add_relation(self, relation_type: str, target_class: str, source_multiplicity: UMLMultiplicity = None, target_multiplicity: UMLMultiplicity = None):
        relation = UMLRelation("", target_class, relation_type, 
                               source_multiplicity or UMLMultiplicity(), 
                               target_multiplicity or UMLMultiplicity())
        self.relations.append(relation)