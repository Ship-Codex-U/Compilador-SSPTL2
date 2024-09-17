import re

tokens = [
    (r'\bint\b',              'palabra reservada int', 23),
    (r'\bfloat\b',            'palabra reservada float', 24),
    (r'\bprint\b',            'palabra reservada print', 24),
    (r'[ \n\t]+',             None, None),
    (r'[A-Za-z_][A-Za-z0-9_]*','identificador', 0),
    (r'\d+\.\d+',             'real', 2),
    (r'\d+',                  'entero', 1),
    (r'\".*?\"',              'cadena', 3),
    (r'\bint\b|\bfloat\b|\bvoid\b', 'tipo', 4),
    (r'\+',                   'operación suma', 5),
    (r'-',                    'operación suma', 5),
    (r'\*',                   'operación multiplicación', 6),
    (r'/',                    'operación multiplicación', 6),
    (r'<|<=|>|>=',            'operación relación', 7),
    (r'\|\|',                 'operación or', 8),
    (r'&&',                   'operación and', 9),
    (r'!',                    'operación not', 10),
    (r'==|!=',                'operación igualdad', 11),
    (r';',                    'punto y coma', 12),
    (r',',                    'coma', 13),
    (r'\(',                   'paréntesis abierto', 14),
    (r'\)',                   'paréntesis cerrado', 15),
    (r'\{',                   'llave abierta', 16),
    (r'\}',                   'llave cerrada', 17),
    (r'=',                    'asignación', 18),
    (r'\bif\b',               'palabra reservada if', 19),
    (r'\bwhile\b',            'palabra reservada while', 20),
    (r'\breturn\b',           'palabra reservada return', 21),
    (r'\belse\b',             'palabra reservada else', 22),
    (r'\$',                   'símbolo de fin de cadena', 25),
]

class Compiler:
    def __init__(self) -> None:
        pass
    
    @classmethod
    def lexicalAnalyser(cls, code):
        pos = 0
        tokensFound = []

        while pos < len(code):
            match = None
            for token_expr in tokens:
                pattern, tokenType, numType = token_expr
                regex = re.compile(pattern)
                match = regex.match(code, pos)
                if match:
                    lexeme = match.group(0)
                    if tokenType is not None:
                        tokensFound.append((lexeme, tokenType, numType))
                    break
            if not match:
                raise SyntaxError(f"Error léxico en el carácter '{code[pos]}' en la posición {pos}")
            else:
                pos = match.end(0)

        return tokensFound