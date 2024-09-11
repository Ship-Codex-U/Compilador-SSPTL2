class CodeFile:
    def __init__(self) -> None:
        self.__code = ""
        self.__codeLines = []
    
    @property
    def code(self):
        return self.__code
    
    @code.setter
    def code(self, code):
        self.__code = code
        
    @property
    def codeLines(self):
        return self.__codeLines

    @codeLines.setter
    def codeLines(self, newCodeLines):
        if isinstance(newCodeLines, list):  # Verificar si new_items es una lista
            self.__codeLines = newCodeLines
        
        
    def load(self, path):
        try:
            with open(path, 'r') as file:
                
                self.__codeLines = file.readlines()
                self.__code = ''.join(self.__codeLines)
                
            return 1
        
        except Exception as e:
            return 0
    
    def save(self, path):
        try:
            with open(path, 'w') as file:
                    
                if self.__codeLines:
                    file.writelines([line if line.endswith('\n') else line + '\n' for line in self.__codeLines])
                    
            return 1
        
        except Exception as e:
            return 0
