# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform
import pprint

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        
        # INITIALIZE NEW CLASES
        #////////////////////////////////////////////////////////////////
        self.codeFile = CodeFile()
        

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Compilador - SSPTL2"
        description = "Compilador - Proyecto desarrollado para la clase de SSPTL2"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////
        widgets.btn_openFile.clicked.connect(self.openFileAction)
        widgets.btn_saveFile.clicked.connect(self.saveFileAction)
        widgets.btn_generate_code.clicked.connect(self.compilerCode)

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_compiler.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX - Boton Deshabilitado
        #def openCloseLeftBox():
            #UIFunctions.toggleLeftBox(self, True)
        #widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        #widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        
        #Boton Deshabilitado
        #widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))
        
        headers = ["Lexema", "Token", "Tipo"]
        widgets.lexical_analizer_table.clear()
        widgets.lexical_analizer_table.setColumnCount(3)
        widgets.lexical_analizer_table.setHorizontalHeaderLabels(headers)
        widgets.lexical_analizer_table.setRowCount(0)
        


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        
        # SHOW COMPILER
        if btnName == "btn_compiler":
            widgets.stackedWidget.setCurrentWidget(widgets.compiler)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        #if btnName == "btn_new":
        #    widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
        #    UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
        #    btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        #if btnName == "btn_save":
        #    print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition().toPoint()


    @Slot( )
    def openFileAction(self):
        mensaje1 = QMessageBox(self)
        mensaje1.setWindowTitle("Alerta.")
        mensaje1.setText("El archivo no se pudo abrir correctamente")
        mensaje1.setStandardButtons(QMessageBox.Ok)
        mensaje1.setDefaultButton(QMessageBox.Ok)
        mensaje1.setIcon(QMessageBox.Critical)
        
        documents_directory = os.path.expanduser("~")
        
        path = QFileDialog.getOpenFileName(
            self,
            'Abrir Archivo',
            documents_directory,
            'TXT (*.txt)'
        )[0]
        
        if self.codeFile.load(path):            
            self.ui.plainTextEdit_editor.clear()
            
            file_content = ''.join(self.codeFile.codeLines)
            self.ui.plainTextEdit_editor.setPlainText(file_content)
        else: 
            mensaje1.exec()
    
    @Slot( )    
    def saveFileAction(self):
        mensaje1 = QMessageBox(self)
        mensaje1.setWindowTitle("Alerta.")
        mensaje1.setText("El archivo no se pudo guardar en la ubicacion seleccionada")
        mensaje1.setStandardButtons(QMessageBox.Ok)
        mensaje1.setDefaultButton(QMessageBox.Ok)
        mensaje1.setIcon(QMessageBox.Critical)
        
        mensaje2 = QMessageBox(self)
        mensaje2.setWindowTitle("Notificacion.")
        mensaje2.setText("Archivo guardado exitosamente")
        mensaje2.setStandardButtons(QMessageBox.Ok)
        mensaje2.setDefaultButton(QMessageBox.Ok)
        mensaje2.setIcon(QMessageBox.Information)
        
        documents_directory = os.path.expanduser("~")
        
        path = QFileDialog.getSaveFileName(
            self,
            'Guardar Archivo',
            documents_directory,
            'TXT (*.txt)'
        )[0]
        
        text = self.ui.plainTextEdit_editor.toPlainText()
        codeLines = text.splitlines()
        self.codeFile.codeLines = codeLines

        if self.codeFile.save(path):
            mensaje2.exec()
        else: 
            mensaje1.exec()
            
    
    @Slot()            
    def compilerCode(self):
        
        self.ui.message_output.clear()
        text = self.ui.plainTextEdit_editor.toPlainText()
                
        tokensFound, lexicalErrors = Compiler.lexicalAnalyser(text)
        
        self.ui.lexical_analizer_table.setRowCount(len(tokensFound))
        
        for pos, (lexema, tokenType, numType) in enumerate(tokensFound):
            lexemaWidget = QTableWidgetItem(str(lexema))
            tokenTypeWidget = QTableWidgetItem(str(tokenType))
            numTypeWidget = QTableWidgetItem(str(numType))
            
            self.ui.lexical_analizer_table.setItem(pos, 0, lexemaWidget)
            self.ui.lexical_analizer_table.setItem(pos, 1, tokenTypeWidget)
            self.ui.lexical_analizer_table.setItem(pos, 2, numTypeWidget)
            
        if(lexicalErrors):
            for i, error in enumerate(lexicalErrors):
                self.showMessageOutput(f'{str(i + 1)}) {error}', QColor(230,25,25))
        else:
            self.showMessageOutput("Lexical analysis completed with no errors", QColor("green"))            
            
            parseErrors = Compiler.parse(tokensFound)
            if(parseErrors):
                for i, error in enumerate(parseErrors):
                    self.showMessageOutput( f'{str(i + 1)}) {error}', QColor(230,25,25))
            else:
                self.showMessageOutput("Syntax analysis completed with no errors", QColor("green"))
                
                semanticErrors = Compiler.semanticAnalyser()
                if(semanticErrors):
                    for i, error in enumerate(semanticErrors):
                        self.showMessageOutput( f'{str(i + 1)}) {error}', QColor(230,25,25))
                else:
                    self.showMessageOutput("Semantic analysis completed with no errors", QColor("green")) 
                                        
                    if self.ui.plainTextEdit_editor.toPlainText().strip():
                        resultMIPS = Compiler.MIPSGenerate(text)
                        resultCode = Compiler.CodeResultGenerate(text)
                        
                        self.MIPSWindow = ResultCompilerWindow(resultMIPS, resultCode)
                        self.MIPSWindow.show()               
                    
    def showMessageOutput(self, text, color):
        # Obtencion del cursor actual
        cursor = self.ui.message_output.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Creacion del formato con el color solicitado
        char_format = QTextCharFormat()
        char_format.setForeground(color)

        # Aplicacion del formato anterior al texto
        cursor.setCharFormat(char_format)
        cursor.insertText(text + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
