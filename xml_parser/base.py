import struct

# Based on https://github.com/koutto/dotnet-binary-deserializer/

class Record(object):
    """Classe de base pour tous les enregistrements XML"""
    records: dict = dict()

    @classmethod
    def add_records(cls, records: list) -> None:
        """Ajoute des enregistrements au registre global
        
        Args:
            records (list): Liste des classes d'enregistrements à ajouter
        """
        for r in records:
            Record.records[r.type] = r

    def __init__(self, type: int = None) -> None:
        """Initialise un enregistrement
        
        Args:
            type (int, optional): Type de l'enregistrement. Defaults to None.
        """
        if type:
            self.type: int = type

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return struct.pack('<B', self.type)

    def __repr__(self) -> str:
        """Représentation en chaîne de caractères de l'enregistrement
        
        Returns:
            str: Représentation de l'enregistrement
        """
        args = ['type=0x%X' % self.type]
        return '<%s(%s)>' % (type(self).__name__, ','.join(args))

    def to_string(self, records: str, skip: int = 0, first_call: bool = True, output: str = "") -> tuple[bool, str]:
        """Convertit une liste d'enregistrements en chaîne XML
        
        Args:
            records (list): Liste des enregistrements à convertir
            skip (int, optional): Nombre d'espaces à ajouter. Defaults to 0.
            first_call (bool, optional): Appel initial de la fonction. Defaults to True.
            output (str, optional): Chaîne de sortie. Defaults to "".
            
        Returns:
            tuple[bool, str]: Tuple contenant un booléen indiquant s'il y a eu un saut de ligne et la chaîne XML
        """
        if records is None:
            return False, output
        was_el = False
        for r in records:
            if isinstance(r, EndElementRecord):
                continue
            if isinstance(r, Element):
                output += ('\r\n' if not first_call else '') + ' ' * skip + str(r)
            else:
                output += str(r)
            new_line = False
            if hasattr(r, 'childs'):
                new_line, output = self.to_string(r.childs, skip+1, False, output)
            if isinstance(r, Element):
                if new_line:
                    output += '\r\n' + ' ' * skip
                if hasattr(r, 'prefix'):
                    output += f'</{r.prefix}:{r.name}>'
                else:
                    output += f'</{r.name.strip()}>'
                was_el = True
            else:
                was_el = False
        return was_el, output

    @classmethod
    def parse(cls, fp) -> list:
        """Parse un flux de bytes en enregistrements XML
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            list: Liste des enregistrements parsés
        """
        if cls != Record:
            return cls()
        root: list = []
        parents: list = []
        last_el: Element = None
        type: int = True
        records: list = root
        while type:
            type = fp.read(1)
            if type:
                type = struct.unpack('<B', type)[0]
                if type in Record.records:
                    obj = Record.records[type].parse(fp)
                    if isinstance(obj, EndElementRecord):
                        if len(parents) > 0:
                            records = parents.pop()
                    elif isinstance(obj, Element):
                        last_el = obj
                        records.append(obj)
                        parents.append(records)
                        obj.childs = []
                        records = obj.childs
                    elif isinstance(obj, Attribute) and last_el:
                        last_el.attributes.append(obj)
                    else:
                        records.append(obj)
                elif type-1 in Record.records:
                    records.append(Record.records[type-1].parse(fp))
                    last_el = None
                    if len(parents) > 0:
                        records = parents.pop()
        return root

class Element(Record):
    """Classe pour les éléments XML"""
    pass

class EndElementRecord(Element):
    """Classe pour les enregistrements de fin d'élément"""
    type = 0x01

class Text(Record):
    """Classe pour les enregistrements de texte"""
    pass

class Attribute(Record):
    """Classe pour les enregistrements d'attribut"""
    pass
