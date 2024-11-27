from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFrame
from Ventana1_ui import Ui_Form

class ResultCompilerWindow(QWidget, Ui_Form):
    def __init__(self, resultMIPS = "No Data", resultCode = "No Data"):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Resultado - Compilador SSPTL2")  
        
        self.OutMIPS_plainTextEdit.setPlainText(resultMIPS)
        self.OutResult_plainTextEdit.setPlainText(resultCode)
        

        
        