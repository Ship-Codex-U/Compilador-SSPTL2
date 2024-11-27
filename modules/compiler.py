import re

class Interpreter:
    def __init__(self, code):
        self.symbol_table = {}  # Tabla de símbolos para almacenar las variables y sus valores
        self.declarations = self.parse_code(code)  # Declaraciones del código fuente
        self.output = []  # Almacena los resultados de las instrucciones print
        self.evaluate()
    
    def evaluate(self):
        """Evalúa todas las declaraciones y realiza las operaciones necesarias."""
        for decl in self.declarations:
            if decl['type'] == 'declaration':
                self.declare_variable(decl)
            elif decl['type'] == 'assignment':
                self.process_assignment(decl)
            elif decl['type'] == 'print':
                self.process_print(decl)
    
    def declare_variable(self, decl):
        """Declara una variable y la inicializa con su valor inicial."""
        var_name = decl['name']
        var_type = decl['var_type']
        # Inicializa con 0 o 0.0 según el tipo si no tiene una asignación inmediata
        initial_value = 0 if var_type == 'int' else 0.0
        self.symbol_table[var_name] = initial_value
    
    def process_assignment(self, decl):
        """Procesa una asignación, evalúa la expresión y actualiza la tabla de símbolos."""
        var_name = decl['name']
        expression = decl['expression_type']
        # Evalúa la expresión y actualiza la tabla de símbolos
        self.symbol_table[var_name] = self.evaluate_expression(expression)
    
    def evaluate_expression(self, expr):
        """Evalúa una expresión y devuelve el resultado."""
        # Reemplaza las variables con sus valores actuales en la tabla de símbolos
        for var in self.symbol_table:
            expr = expr.replace(var, str(self.symbol_table[var]))
        
        # Evalúa la expresión aritmética
        try:
            result = eval(expr)
            # Determina si el resultado debe ser entero o flotante
            return int(result) if result == int(result) else float(result)
        except Exception as e:
            raise ValueError(f"Error evaluando la expresión '{expr}': {e}")
    
    def process_print(self, decl):
        """Procesa una instrucción print y almacena el valor en la salida."""
        var_name = decl['name']
        if var_name in self.symbol_table:
            value = self.symbol_table[var_name]
            self.output.append(f"{var_name} = {value}")
        else:
            raise ValueError(f"Error: La variable '{var_name}' no está definida.")
    
    def parse_code(cls, code):
        lines = code.strip().splitlines()

        declarations = []
        variables = {}  # Diccionario para almacenar variables y sus tipos

        for line in lines:
            line = line.strip()

            # Declaración e inicialización (e.g., int suma = 0;)
            decl_init_match = re.match(r"(int|float|double|char)\s+(\w+)\s*=\s*(.+);", line)
            if decl_init_match:
                var_type, name, expression = decl_init_match.groups()
                variables[name] = var_type  # Registrar el tipo de la variable
                declarations.append({
                    'type': 'declaration',
                    'name': name,
                    'var_type': var_type
                })
                declarations.append({
                    'type': 'assignment',
                    'name': name,
                    'var_type': var_type,
                    'expression_type': expression
                })
                continue

            # Declaración sin inicialización (e.g., int x;)
            decl_match = re.match(r"(int|float|double|char)\s+(\w+);", line)
            if decl_match:
                var_type, name = decl_match.groups()
                variables[name] = var_type  # Registrar el tipo de la variable
                declarations.append({
                    'type': 'declaration',
                    'name': name,
                    'var_type': var_type
                })
                continue

            # Asignación (e.g., suma = x + y + 30;)
            assign_match = re.match(r"(\w+)\s*=\s*(.+);", line)
            if assign_match:
                name, expression = assign_match.groups()
                var_type = variables.get(name, 'int')  # Obtener el tipo de la variable si está registrado
                declarations.append({
                    'type': 'assignment',
                    'name': name,
                    'var_type': var_type,
                    'expression_type': expression
                })
                continue

            # Print (e.g., print(suma);)
            print_match = re.match(r"print\((\w+)\);", line)
            if print_match:
                name = print_match.group(1)
                var_type = variables.get(name, 'unknown')  # Obtener el tipo de la variable o marcar como desconocido
                declarations.append({
                    'type': 'print',
                    'name': name,
                    'var_type': var_type
                })
                continue

        return declarations
    
    
    def getResult(self):
        """Devuelve el resultado de todas las instrucciones print."""
        return "\n".join(self.output)

class MIPSCodeGenerator:
    def __init__(self, code):
        self.declarations = self.parse_code(code)
        self.mips_code = [] 
        self.result = self.generate()

    def generate(self):
        # Sección de datos
        self.mips_code.append(".data")
        for decl in self.declarations:
            if decl['type'] == 'declaration':
                if decl['var_type'] == 'int':
                    self.mips_code.append(f"{decl['name']}: .word 0")
                elif decl['var_type'] == 'float':
                    self.mips_code.append(f"{decl['name']}: .float {decl.get('initial_value', 0.0)}")

        # Sección de texto
        self.mips_code.append("\n.text")
        self.mips_code.append("main:")

        for decl in self.declarations:
            if decl['type'] == 'assignment':
                self.process_assignment(decl)
            elif decl['type'] == 'print':
                self.process_print(decl)

        # Finalizar programa
        self.mips_code.append("    li $v0, 10")
        self.mips_code.append("    syscall")

        return "\n".join(self.mips_code)

    def process_assignment(self, decl):
        """Procesa asignaciones, incluyendo expresiones complejas con variables y literales."""
        expr = decl['expression_type']
        var_type = decl['var_type']
        operators = re.findall(r'[+\-*/]', expr)  # Encuentra todos los operadores
        operands = re.split(r'[+\-*/]', expr)  # Divide la expresión en operandos

        if var_type == 'int':
            self.distribute_registers_int(operands, operators, decl['name'])
        elif var_type == 'float':
            self.distribute_registers_float(operands, operators, decl['name'])

    def distribute_registers_int(self, operands, operators, result_var):
        """Distribuye cálculos entre registros temporales para enteros."""
        self.load_operand(operands[0].strip(), '$t0')  # Carga el primer operando en $t0

        for i, op in enumerate(operators):
            reg_target = f'$t{i + 1}'  # Usa $t1, $t2, etc., dinámicamente
            self.load_operand(operands[i + 1].strip(), reg_target)  # Carga el siguiente operando
            instr = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}[op]
            self.mips_code.append(f"    {instr} $t0, $t0, {reg_target}")  # Actualiza $t0 con el resultado

        self.mips_code.append(f"    sw $t0, {result_var}")  # Guarda el resultado final en memoria

    def distribute_registers_float(self, operands, operators, result_var):
        """Distribuye cálculos entre registros temporales para flotantes."""
        self.load_operand(operands[0].strip(), '$f0', is_float=True)  # Carga el primer operando en $f0

        for i, op in enumerate(operators):
            reg_target = f'$f{i + 1}'  # Usa $f1, $f2, etc., dinámicamente
            self.load_operand(operands[i + 1].strip(), reg_target, is_float=True)  # Carga el siguiente operando
            instr = {'+': 'add.s', '-': 'sub.s', '*': 'mul.s', '/': 'div.s'}[op]
            self.mips_code.append(f"    {instr} $f0, $f0, {reg_target}")  # Actualiza $f0 con el resultado

        self.mips_code.append(f"    s.s $f0, {result_var}")  # Guarda el resultado final en memoria

    def load_operand(self, operand, reg, is_float=False):
        """Carga un operando en un registro, ya sea una variable o un literal."""
        if operand.isdigit() or '.' in operand:  # Literal
            if is_float:
                self.mips_code.append(f"    li.s {reg}, {operand}")
            else:
                self.mips_code.append(f"    li {reg}, {operand}")
        else:  # Variable
            if is_float:
                self.mips_code.append(f"    l.s {reg}, {operand}")
            else:
                self.mips_code.append(f"    lw {reg}, {operand}")

    def process_print(self, decl):
        """Procesa la impresión de valores."""
        var_type = decl['var_type']
        if var_type == 'int':
            self.mips_code.append(f"    lw $a0, {decl['name']}")
            self.mips_code.append("    li $v0, 1")  # Código de sistema para imprimir enteros
        elif var_type == 'float':
            self.mips_code.append(f"    l.s $f12, {decl['name']}")
            self.mips_code.append("    li $v0, 2")  # Código de sistema para imprimir flotantes
        self.mips_code.append("    syscall")

    def parse_code(cls, code):
        lines = code.strip().splitlines()

        declarations = []
        variables = {}  # Diccionario para almacenar variables y sus tipos

        for line in lines:
            line = line.strip()

            # Declaración e inicialización (e.g., int suma = 0;)
            decl_init_match = re.match(r"(int|float|double|char)\s+(\w+)\s*=\s*(.+);", line)
            if decl_init_match:
                var_type, name, expression = decl_init_match.groups()
                variables[name] = var_type  # Registrar el tipo de la variable
                declarations.append({
                    'type': 'declaration',
                    'name': name,
                    'var_type': var_type
                })
                declarations.append({
                    'type': 'assignment',
                    'name': name,
                    'var_type': var_type,
                    'expression_type': expression
                })
                continue

            # Declaración sin inicialización (e.g., int x;)
            decl_match = re.match(r"(int|float|double|char)\s+(\w+);", line)
            if decl_match:
                var_type, name = decl_match.groups()
                variables[name] = var_type  # Registrar el tipo de la variable
                declarations.append({
                    'type': 'declaration',
                    'name': name,
                    'var_type': var_type
                })
                continue

            # Asignación (e.g., suma = x + y + 30;)
            assign_match = re.match(r"(\w+)\s*=\s*(.+);", line)
            if assign_match:
                name, expression = assign_match.groups()
                var_type = variables.get(name, 'int')  # Obtener el tipo de la variable si está registrado
                declarations.append({
                    'type': 'assignment',
                    'name': name,
                    'var_type': var_type,
                    'expression_type': expression
                })
                continue

            # Print (e.g., print(suma);)
            print_match = re.match(r"print\((\w+)\);", line)
            if print_match:
                name = print_match.group(1)
                var_type = variables.get(name, 'unknown')  # Obtener el tipo de la variable o marcar como desconocido
                declarations.append({
                    'type': 'print',
                    'name': name,
                    'var_type': var_type
                })
                continue

        return declarations
    
    def getResult(self):
        return self.result
    
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # Tabla de símbolos: almacena nombre y tipo de cada variable
        self.semantic_errors = []  # Lista para almacenar errores semánticos
        self.declarations = []

    def declare_variable(self, name, var_type):
        """Declara una variable en la tabla de símbolos; registra un error si ya está declarada."""
        if name in self.symbol_table:
            self.semantic_errors.append(f"Error SEMANTICO: La variable '{name}' ya ha sido declarada.")
        else:
            self.symbol_table[name] = var_type

    def check_variable(self, name):
        """Verifica si una variable ha sido declarada antes de usarse; registra un error si no lo está."""
        print(f"check_variable | variable a checar -> {name}, name not in self.symbol_table -> {name not in self.symbol_table}")
        if name not in self.symbol_table:
            self.semantic_errors.append(f"Error SEMANTICO: La variable '{name}' no ha sido declarada.")
            print(self.semantic_errors)
        else:
            return self.symbol_table[name]

    def check_type(self, name, expected_type):
        """Verifica que el tipo de una variable coincida con el tipo esperado."""
        actual_type = self.symbol_table.get(name)
        if actual_type and actual_type != expected_type:
            self.semantic_errors.append(
                f"Error SEMANTICO: Se esperaba un dato de tipo '{actual_type}' pero se encontró el siguiente tipo de valor '{expected_type}' para la variable '{name}'."
            )
    
    def check_assignment(self, var_name, expr_type):
        """Verifica que el tipo de la variable coincida con el tipo de la expresión asignada."""
        var_type = self.symbol_table.get(var_name)
        if var_type and var_type != expr_type:
            if var_type == "int" and expr_type == "float":
                self.semantic_errors.append(
                    f"Error SEMANTICO: No se puede asignar un valor de tipo 'float' a la variable '{var_name}' de tipo 'int'."
                )
            elif var_type == "float" and expr_type == "int":
                # Si es permitido en tu lenguaje, podrías omitir este caso
                pass
            else:
                self.semantic_errors.append(
                    f"Error SEMANTICO: El tipo de la expresión ('{expr_type}') no coincide con el tipo de la variable '{var_name}' ('{var_type}')"
                )

    def analyze(self):
        """Método principal para iniciar el análisis semántico, tomando como entrada el parser."""
        for declaration in self.declarations:
            if declaration['type'] == 'declaration':
                self.declare_variable(declaration['name'], declaration['var_type'])
            elif declaration['type'] == 'assignment':
                self.check_variable(declaration['name'])
                if declaration['expression_type']:
                    self.check_type(declaration['name'], declaration['expression_type'])
                    
    def add_errors(self, error):
        self.semantic_errors.append(error)

    def get_errors(self):
        """Devuelve los errores semánticos encontrados."""
        return self.semantic_errors

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = 0
        self.errors = []
        self.line_number = 1  # Rastrea el número de línea actual
        self.semantic_analyzer = SemanticAnalyzer()
        self.declarations = []
        
    def get_equivalent(self, word):
        equivalent = {
            "entero": "int",
            "real": "float",
        }
        
        print(f" Equivalencias | recibido = {word}, equivalente = {equivalent.get(word, word)} " )
        
        return equivalent.get(word, word)

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
                self.errors.append(f"Error SINTACTICO: se esperaba '{expected_token_type}' pero se encontró '{token[1]}'")
        elif expected_token_type in ("paréntesis abierto", "paréntesis cerrado", "llave abierta", "llave cerrada", ""):
            self.errors.append(f"Error SINTACTICO: se esperaba '{expected_token_type}'")
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
            self.errors.append(f"Error SINTACTICO: declaración inválida")
            tipo = self.get_next_token()
        
        print(f'termino')
        
    
    def DeclaracionVar(self):
        """Procesa una declaración de variable"""
        tipo = self.get_next_token()  # tipo: int o float
        ident_token = self.peek_token()
                
        if ident_token[1] == 'identificador':
            var_name = ident_token[0]
            self.get_next_token()  # Consume el identificador
        
            expr_type = None
            
            if self.peek_token() and self.peek_token()[1] == 'asignación':
                self.get_next_token()  # Consumes el token '='
                expr_type = self.Expresion()
                
                print(f"Tipo expresion DeclaracionVar -> {expr_type}")
            
            print(f"DeclaracionVar semantic_error -> {self.semantic_analyzer.get_errors()}")
                            
            self.semantic_analyzer.declare_variable(var_name, self.get_equivalent(expr_type))
        
        if not self.match('punto y coma'):
            self.errors.append(f"Error SINTACTICO: falta ';' al final de la declaración")
    
    def Asignacion(self):
        """Procesa una asignación a una variable"""
        token = self.peek_token()
        
        if token and token[1] == 'identificador':
            var_name = token[0]
            print(self.semantic_analyzer.symbol_table)
            self.semantic_analyzer.check_variable(var_name)  # Verifica que la variable esté declarada
            self.get_next_token()  # Consume el identificador
        else:
            self.errors.append(f"Error SINTACTICO: el lado izquierdo de una asignación debe ser un identificador, pero se encontró '{token[1]}'")
            self.get_next_token()  # Avanzar para evitar que se quede atascado

        self.match('asignación')  # =
        if self.peek_token() and self.peek_token()[1] != 'punto y coma':
            expr_type = self.Expresion()  # Procesa la expresión solo si hay algo diferente de un ';'
            
            self.semantic_analyzer.declarations.append({
                'type': 'assignment',
                'name': var_name,
                'expression_type': self.get_equivalent(expr_type)  # Tipo de la expresión asignada
            })
            
            self.semantic_analyzer.check_assignment(var_name, self.get_equivalent(expr_type))
            
        else:
            self.errors.append(f"Error SINTACTICO: se esperaba una expresión después de '='")
        self.match('punto y coma')

    def Expresion(self):
        """Procesa una expresión aritmética o lógica y devuelve el tipo resultante."""
        term_type = self.Termino()  # Obtiene el tipo del término inicial
        expr_prime_type = self.ExpresionPrime()  # Obtiene el tipo de la parte restante de la expresión

        # Determina el tipo final de la expresión
        if term_type == 'real' or expr_prime_type == 'real':
            return 'real'  # Si alguno de los tipos es real, la expresión es de tipo real
        
        
        return term_type  # De lo contrario, conserva el tipo original

    def ExpresionPrime(self):
        """Procesa el resto de una expresión y devuelve el tipo resultante, soportando + o -."""
        token = self.peek_token()
        if token and token[1] in ['operación suma', 'operación resta', 'operación multiplicación', 'operación división']:
            self.get_next_token()  # Consume el operador
            term_type = self.Termino()  # Obtiene el tipo del siguiente término
            expr_prime_type = self.ExpresionPrime()  # Recursivamente obtiene el tipo de ExpresionPrime

            # Si cualquier parte es de tipo real, el resultado es real
            if term_type == 'real' or expr_prime_type == 'real' or self.get_equivalent(term_type) == 'float' or self.get_equivalent(expr_prime_type) == 'float':
                return 'real'
            return term_type  # Si ambos son enteros, el resultado es entero
        return None

    def Termino(self):
        """Procesa un término en la expresión (maneja multiplicación o división)"""
        factor_type = self.Factor()  # Obtiene el tipo del factor inicial
        term_prime_type = self.TerminoPrime()  # Obtiene el tipo de la parte restante del término

        # Si alguno de los factores es real, el término es de tipo real
        if factor_type == 'real' or term_prime_type == 'real':
            return 'real'
        
        return factor_type

    def TerminoPrime(self):
        """Procesa el resto de un término, soportando * o /"""
        token = self.peek_token()
        if token and token[1] in ['operación multiplicación', 'operación division']:
            op = token[1]  # Captura el operador actual
            self.get_next_token()  # Consumimos el token * o /
            factor_type = self.Factor()  # Obtiene el tipo del siguiente factor
            term_prime_type = self.TerminoPrime()  # Recursivamente obtiene el tipo de TerminoPrime
            
            # Si cualquiera es de tipo real, el resultado es real
            if factor_type == 'real' or term_prime_type == 'real' or self.get_equivalent(factor_type) == "float" or self.get_equivalent(term_prime_type) == "float":
                return 'real'
            
            return factor_type  # Si ambos son enteros, el resultado es entero
        return None  # No hay más operaciones, así que no afecta el tipo

    def Factor(self):
        """Procesa un factor: número, identificador o expresión entre paréntesis"""
        token = self.peek_token()

        if token:
            if token[1] == 'entero':
                self.get_next_token()  # Consume el número entero
                return 'int'
            elif token[1] == 'real':
                self.get_next_token()  # Consume el número real
                return 'float'
            elif token[1] == 'identificador':
                var_name = token[0]
                var_type = self.semantic_analyzer.check_variable(var_name)  # Verifica y obtiene el tipo
                
                print(f" Factor | var_name = {var_name}, var_type = {var_type} " )
                self.get_next_token()  # Consume el identificador
                return var_type  # Retorna el tipo de la variable desde la tabla de símbolos
            elif token[1] == 'paréntesis abierto':
                self.get_next_token()  # Consume '('
                expr_type = self.Expresion()  # Llama recursivamente a Expresion
                self.match('paréntesis cerrado')
                return expr_type
        return None

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
            self.errors.append(f"Error SINTACTICO: se esperaba un operador de relación o igualdad'")
        
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
    (r'/',                    'operación división', 6),
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
    parseData = None
    semanticErrors = None
    declarations = []
    
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
                error_message = f"Error LEXICO: token no reconosido '{code[pos]}'"
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
        
        cls.parseData = parse
        cls.semanticErrors = parse.semantic_analyzer.get_errors()

        
        return parse.get_errors()
    
    @classmethod
    def semanticAnalyser(cls):
        return cls.semanticErrors
    
    @classmethod
    def MIPSGenerate(cls, code):
        MIPSCode = MIPSCodeGenerator(code)
        
        return MIPSCode.getResult()
    
    @classmethod
    def CodeResultGenerate(cls, code):
        ResultCode = Interpreter(code)
        
        return ResultCode.getResult()
    
    