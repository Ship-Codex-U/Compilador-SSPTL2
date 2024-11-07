import re

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # Tabla de símbolos: almacena nombre y tipo de cada variable
        self.semantic_errors = []  # Lista de errores semánticos

    def declare_variable(self, name, var_type):
        """Declara una variable en la tabla de símbolos si no existe; si ya existe, reporta error."""
        if name in self.symbol_table:
            self.semantic_errors.append(f"Error semántico: La variable '{name}' ya ha sido declarada.")
        else:
            self.symbol_table[name] = var_type  # Guarda el nombre y tipo de la variable

    def check_variable(self, name):
        """Verifica si una variable ha sido declarada antes de su uso."""
        if name not in self.symbol_table:
            self.semantic_errors.append(f"Error semántico: La variable '{name}' no ha sido declarada.")

    def check_type(self, name, expected_type):
        """Verifica que el tipo de una variable coincida con el tipo esperado."""
        actual_type = self.symbol_table.get(name)
        if actual_type and actual_type != expected_type:
            self.semantic_errors.append(
                f"Error semántico: Se esperaba '{expected_type}' pero se encontró '{actual_type}' para la variable '{name}'."
            )

    def get_errors(self):
        """Devuelve la lista de errores semánticos."""
        return self.semantic_errors

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = 0
        self.errors = []
        self.line_number = 1  # Rastrea el número de línea actual
        self.semantic_analyzer = SemanticAnalyzer()

    def get_next_token(self):
        if self.current_token < len(self.tokens):
            token = self.tokens[self.current_token]
            self.current_token += 1
            # Si el token contiene un salto de línea, actualizamos el número de línea
            if r'\n' in token[0]:
                self.line_number += token[0].count(r'\n')
            return token
        else:
            return None

    def peek_token(self):
        """Retorna el token actual sin avanzar o None si no hay más tokens"""
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token]
        return None

    def match(self, expected_token_type):
        """Verifica si el token actual coincide con el esperado y avanza"""
        token = self.peek_token()
        
        print(f'Match: token actual -> {token} == token a comparar { expected_token_type}')
        if token:  # Verificamos si el token no es None
            if token[1] == expected_token_type:
                print('yes')
                return self.get_next_token()  # Si coincide, avanzamos
            else:
                print('no')
                print('error a cargar')
                self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba '{expected_token_type}' pero se encontró '{token[1]}'")
        elif expected_token_type in ("paréntesis abierto", "paréntesis cerrado", "llave abierta", "llave cerrada", ""):
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba '{expected_token_type}'")
        #else:
            # self.errors.append(f"Error sintáctico: se esperaba '{expected_token_type}' pero no se encontró ningún token (final prematuro del código)")
        return None

    def Programa(self):
        """Regla inicial de la gramática"""
        while self.peek_token():  # Mientras haya tokens
            self.Declaracion()
        
        print("--------- Termino de leer todo el programa -----------")

    def Declaracion(self):
        """Procesa una declaración, ya sea una declaración de variable o asignación"""
        token = self.peek_token()
        print(f'Parse: token en declaracion -> {token}')
        if token and token[1] == 'palabra reservada int' or token[1] == 'palabra reservada float':
            print(f'entro a palabra reservada int o float')
            self.DeclaracionVar()
            print(f'Termino de entrar a palabra reservada int o float')
        elif token and token[1] == 'identificador':
            print(f'entro a identificador')
            self.Asignacion()
        elif token and token[1] == 'palabra reservada if':
            print(f'entro a palabra reservada')
            self.IfElse()
        elif token and token[1] == 'palabra reservada print':
            print(f'entro a palabra reservada print')
            self.printStmt()
        else:
            print(f'entro a error')
            print(f'entro a cargar')
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: declaración inválida")
            tipo = self.get_next_token()
        
        print(f'termino')
        
    
    def DeclaracionVar(self):
        """Procesa una declaración de variable"""
        tipo = self.get_next_token()  # tipo: int o float
        ident_token = self.peek_token()
                
        if ident_token[1] == 'identificador':
            var_name = ident_token[0]
            self.semantic_analyzer.declare_variable(var_name, tipo[1])  # Declara la variable en la tabla de símbolos
            self.get_next_token()  # Consume el identificador
        
            if self.peek_token() and self.peek_token()[1] == 'asignación':
                self.get_next_token()  # Consumes el token '='
                
                dataType = self.peek_token()
                self.Expresion()

                if not self.are_equivalent(tipo[1], dataType[1]):
                    self.semantic_analyzer.semantic_errors.append(
                        f"Error semántico en la línea {self.line_number}: "
                        f"Se esperaba un valor de tipo '{tipo[0]}' pero se encontró el siguiente tipo de valor {dataType[1]}"
                    )
            else:
                # Si no hay una asignación después de la declaración, no pasa nada
                pass
        
        if not self.match('punto y coma'):
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: falta ';' al final de la declaración")

    def are_equivalent(self, word1, word2):
        mapping = {
            "palabra reservada int": "entero",
            "palabra reservada float": "real",
            "palabra reservada float": "flotante",
        }
        
        return mapping.get(word1) == word2 or mapping.get(word2) == word1
    
    def Asignacion(self):
        """Procesa una asignación a una variable"""
        token = self.peek_token()
        
        if token and token[1] == 'identificador':
            var_name = token[0]
            self.semantic_analyzer.check_variable(var_name)  # Verifica que la variable esté declarada
            self.get_next_token()  # Consume el identificador
        else:
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: el lado izquierdo de una asignación debe ser un identificador, pero se encontró '{token[1]}'")
            self.get_next_token()  # Avanzar para evitar que se quede atascado

        self.match('asignación')  # =
        if self.peek_token() and self.peek_token()[1] != 'punto y coma':
            self.Expresion()  # Procesa la expresión solo si hay algo diferente de un ';'
        else:
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba una expresión después de '='")
        self.match('punto y coma')

    def Expresion(self):
        """Procesa una expresión aritmética o lógica"""
        self.Termino()
        self.ExpresionPrime()

    def ExpresionPrime(self):
        """Procesa el resto de una expresión, soportando + o -"""
        token = self.peek_token()
        if token and token[1] == 'operación suma':  # Puede ser + o -
            self.get_next_token()  # Consumimos el token +
            self.Termino()
            self.ExpresionPrime()  # Llamada recursiva

    def Termino(self):
        """Procesa un término en la expresión (maneja multiplicación o división)"""
        self.Factor()
        self.TerminoPrime()

    def TerminoPrime(self):
        """Procesa el resto de un término, soportando * o /"""
        token = self.peek_token()
        if token and (token[1] == 'operación multiplicación'):
            self.get_next_token()  # Consumimos el token * o /
            self.Factor()
            self.TerminoPrime()

    def Factor(self):
        """Procesa un factor: número, identificador o expresión entre paréntesis"""
        print('Entro al factor')
        token = self.peek_token()
        print(f'Token actual -> {token}')
        if token:
            if token[1] == 'entero' or token[1] == 'real':
                print('entro a entero o real')
                self.get_next_token()  # Consumimos el número
            elif token[1] == 'identificador':
                print('entro a identificado')
                self.get_next_token()  # Consumimos el identificador
            elif token[1] == 'paréntesis abierto':
                print('entro a paréntesis abierto')
                self.get_next_token()  # Consumimos el '('
                self.Expresion()       # Llamada recursiva a Expresion
                self.match('paréntesis cerrado')
            else:
                self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba un número, identificador o '(', pero se encontró {token}")
        else:
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba un número, identificador o '(', pero no se encontró ningún token")

    def IfElse(self):
        """Procesa la estructura if-else"""
        print(f'Procesando if')
        
        
        self.match('palabra reservada if')
        print("paso if")
        self.match('paréntesis abierto')
        print("paso pa")
        
        print('Entro prueba expresion relacional')
        self.ExpresionRelacional()
        print('paso prueba expresion relacional')
        
        self.match('paréntesis cerrado')
        print("paso pc")
        self.match('llave abierta')
        print("paso la")
        
        
        while self.peek_token() and self.peek_token()[1] != 'llave cerrada':
            self.Declaracion()
        self.match('llave cerrada')
        token = self.peek_token()
        if token and token[1] == 'palabra reservada else':
            self.get_next_token()  # Consumimos else
            self.match('llave abierta')
            while self.peek_token() and self.peek_token()[1] != 'llave cerrada':
                self.Declaracion()
            self.match('llave cerrada')

    def ExpresionRelacional(self):
        """Procesa una expresión relacional (por ejemplo, ==)"""
        self.Expresion()  # Procesa el lado izquierdo
        
        token = self.peek_token()  # Vemos el operador sin avanzar
        if token and (token[1] == 'operación igualdad' or token[1] == 'operación relación'):
            self.get_next_token()  # Consumimos el operador de relación o igualdad
        else:
            self.errors.append(f"Error sintáctico en la línea {self.line_number}: se esperaba un operador de relación o igualdad'")
        
        self.Expresion()  # Procesa el lado derecho

    def printStmt(self):
        """Procesa la declaración print"""
        self.match('palabra reservada print')
        self.match('paréntesis abierto')
        self.Expresion()
        self.match('paréntesis cerrado')
        self.match('punto y coma')

    def get_errors(self):
        """Devuelve la lista de errores"""
        return self.errors

    def get_semantic_errors(self):
        """Devuelve los errores semánticos encontrados."""
        return self.semantic_analyzer.get_errors()

tokens = [
    (r'\bint\b',              'palabra reservada int', 23),
    (r'\bfloat\b',            'palabra reservada float', 24),
    (r'\bprint\b',            'palabra reservada print', 24),
    (r'\bif\b',               'palabra reservada if', 19),
    (r'\belse\b',             'palabra reservada else', 22),
    (r'\bint\b|\bfloat\b|\bvoid\b', 'tipo', 4),
    (r'[ \n\t]+',             None, None),                      # Para ignorar los espacios en blanco
    (r'[A-Za-z_][A-Za-z0-9_]*','identificador', 0),
    (r'\d+\.\d+',             'real', 2),
    (r'\d+',                  'entero', 1),
    (r'\".*?\"',              'cadena', 3),
    (r'\+',                   'operación suma', 5),
    (r'-',                    'operación resta', 5),
    (r'\*',                   'operación multiplicación', 6),
    (r'/',                    'operación division', 6),
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
]

class Compiler:
    semanticErrors = []
    
    def __init__(self) -> None:
        pass
    
    @classmethod
    def lexicalAnalyser(cls, code):
        # Compilar los patrones de tokens en una sola expresión regular
        token_regex = '|'.join(f'(?P<TOKEN_{i}>{pattern})' for i, (pattern, _, _) in enumerate(tokens))
        compiled_re = re.compile(token_regex)
        
        print(token_regex)
        
        pos = 0
        line_num = 1
        tokensFound = []
        errors = []
        
        print(f'Tamanio del codigo -> {len(code)} \n\n')

        while pos < len(code):
            match = compiled_re.match(code, pos)
            print(f'Esto es el match -> {match}')
            print(f'Pos inicial -> {pos} \n')
            if match:
                for i, (_, tokenType, numType) in enumerate(tokens):
                    lexeme = match.group(f'TOKEN_{i}')
                    print(f'Esto es el lexema -> {lexeme}')
                    print(f'Esto es el tipo de token -> {tokenType}')
                    print(f'Esto es el esto es el numero de tipo -> {numType}')
                    if lexeme:
                        print('Paso la validacion del lexema \n')
                        if tokenType:
                            print('Paso la validacion del tipo de token \n')
                            tokensFound.append((lexeme, tokenType, numType))
                        pos = match.end()  # Avanzamos a la siguiente posición después del token
                        print(f'Pos if -> {pos} \n')
                        line_num += lexeme.count('\n')  # Actualizamos el número de línea si hay saltos de línea
                        break
            else:
                error_message = f"Lexical error on line {line_num}: unrecognized token '{code[pos]}'"
                errors.append(error_message)
                pos += 1  # Avanzamos la posición para evitar quedarse atrapado en un ciclo
                print(f'Pos else -> {pos} \n')
                if code[pos-1] == '\n':
                    line_num += 1
            print(f'Pos final -> {pos} \n')

        return tokensFound, errors
    
    @classmethod
    def parse(cls, tokensFound):        
        parse = Parser(tokensFound)
        parse.Programa()
        cls.semanticErrors = parse.get_semantic_errors()
        
        print(cls.semanticErrors)
        
        return parse.get_errors()
    
    @classmethod
    def semanticAnalyser(cls):
        return cls.semanticErrors
        
        