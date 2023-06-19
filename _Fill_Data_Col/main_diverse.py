#Das ist das Hauptprogramm, um neue verben in der daten colection abzuspeichern

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QTextEdit, QAction, QFileDialog
import sys
import os
import json
import numpy as np
from bs4 import BeautifulSoup

sys.path.append("_Fill_Data_Col")

from save_exc_lib import OpenExcel
from qt5_tools import SearchInput, TextEdit, FormatBar, TableOfContents


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
IMAGE_EXTENSIONS = ['.jpg','.png','.bmp']
HTML_EXTENSIONS = ['.htm', '.html']

def hexuuid():
    return uuid.uuid4().hex

def splitext(p):
    return os.path.splitext(p)[1].lower()

class MainWindow(QMainWindow):
    def __init__(self, verbs_con_ordner, editor=False, format_vorlage=False):
        super().__init__()
        self.editor_bool = editor
        self.aktiv_folder = verbs_con_ordner
        if not format_vorlage:
            self.format_vorlage = self.open_info_js(self.aktiv_folder)
        else:
            self.format_vorlage = format_vorlage
        
        self.all_editors = []
        self.init_start()
        
            
        
        #The whole Windows layout...............................
        # Erstelle ein vertikales Layout
        layout = QVBoxLayout()
        # Erstellt einen Input für den Namen des Verbs
        layout.addWidget(QLabel("Name:"))
        
        # Erstelle ein srollierbaren Bereich mit inputs und labels
        # ScrollWidget erstellen
        scrollWidget = QWidget()
        scrollWidgetLayout = QVBoxLayout(scrollWidget)
        self.inputs_form = {}
        
        if not editor:
            self.input1 = SearchInput(self.all_Names_list)#Tiny Editor
            #print(self.input1.text())
            # Ruft die Funktion auf wenn der Input mit dem Namen fertig geschrieben ist. Also wenn zu nächsten Input gewechselt wird.
            self.input1.editingFinished.connect(self.show_available_data)
            layout.addWidget(self.input1)
            #The layout of the litle inputs
            
            
            for key, value in self.format_vorlage.items():
                input_abs = {}
                #Untertitel == Abschnitstitel
                scrollWidgetLayout.addWidget(QLabel(key+":"))
                
                #Abs_layout = QFormLayout()
                for lable in value:
                    # Erstelle ein Formular-Layout für den Abschnitt "Texteingabe"
                    input_text = QLineEdit()
                    #Wenn der Input fertig ist, also enter gedrückt wird, wird die Funktion aufgerufen
                    input_text.editingFinished.connect(self.save_the_inputs)
                    # create a horizontal layout for each row
                    row_layout = QHBoxLayout()
                    #scrollWidgetLayout.addRow(QLabel(lable), input_text)
                    row_layout.addWidget(QLabel(lable))
                    row_layout.addWidget(input_text)
                    scrollWidgetLayout.addLayout(row_layout)
                    
                    input_abs[lable]=input_text
                self.inputs_form[key] = input_abs
                # Füge einen Abstand von 10 Pixeln hinzu
                scrollWidgetLayout.addSpacing(20)
            # Scrollbereich erstellen
            scrollArea = QScrollArea()
            scrollArea.setWidgetResizable(True)
            scrollArea.setWidget(scrollWidget)
            # Scrollbereich zum Layout hinzufügen
            layout.addWidget(scrollArea)
            
        else:
            # Create a text edit widget            
            self.input1 = TextEdit(self)
            self.input1.setPlaceholderText("Name")
            #Set the fixed height of the editor, in relation to the screen size
            self.input1.setFixedHeight(int(self.height()*0.3))
            self.all_editors.append(self.input1)
            layout.addWidget(self.input1)
            #The layout of the litle inputs
            
            
            for key, value in self.format_vorlage.items():
                input_abs = {}
                #Untertitel == Abschnitstitel
                scrollWidgetLayout.addWidget(QLabel(key+":"))
                
                #Abs_layout = QFormLayout()
                for lable in value:
                    #big Text editor
                    input_text = TextEdit(self)
                    input_text.setPlaceholderText(lable)
                    #Set the size of the editor, width and height. In relation to the screen size
                    input_text.setFixedHeight(int(self.width()*0.65))
                    self.all_editors.append(input_text)
                    scrollWidgetLayout.addWidget(QLabel(lable))#First adds a label at the top
                    scrollWidgetLayout.addWidget(input_text)
                    
                    input_abs[lable]=input_text
                self.inputs_form[key] = input_abs
                # Füge einen Abstand von 10 Pixeln hinzu
                scrollWidgetLayout.addSpacing(20)
            # Scrollbereich erstellen
            scrollArea = QScrollArea()
            scrollArea.setWidgetResizable(True)
            scrollArea.setWidget(scrollWidget)
            # Scrollbereich zum Layout hinzufügen
            layout.addWidget(scrollArea)
            
            #Create a Formatbar in the menulist. Until now you cant say where it should be. It is always at the top.
            self.formatbar = FormatBar(self)
            
            
            container = QWidget()
            container.setLayout(layout)
            self.setCentralWidget(container)

            
        # Add a "Save" action to the file menu
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+s")
        save_action.triggered.connect(self.save_the_inputs)
        
        # Erstelle einen Button
        button = QPushButton("Eingaben lesen")
        button_clear = QPushButton("Eingaben löschen")
        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(button)
        hLayout2.addWidget(button_clear)
        layout.addLayout(hLayout2)

        # Verbinde das clicked-Signal des Buttons mit der Methode read_inputs
        button.clicked.connect(self.save_the_inputs)
        button_clear.clicked.connect(self.clear_the_inputs)
        
        
       # Ganzes Layout HLayout mit dem Layout und dem Inhaltsverzeichnis
        widget_central = QWidget()
        widget_central.setLayout(layout)
        self.table_of_content = TableOfContents(self.content_dict)
        self.table_of_content.table.cellClicked.connect(self.change_show_topic)
        # Ein QSplitter erstellen und das HLayoutWidget hinzufügen
        splitter = QSplitter()
        splitter.addWidget(self.table_of_content)
        splitter.addWidget(widget_central)  # central_widget entsprechend definieren
        # Setze das QSplitter als zentrales Widget des Hauptfensters
        self.setCentralWidget(splitter)

        # Setze den Fenstertitel und zeige das Fenster an
        self.setWindowTitle("Verben Editor")
        self.show()
    
    def init_start(self):
        #Erstellt für jede Zeitform eine OpenExcel Instanz. Oder Zukünfig auch für andere Themen
        self.all_sectors = {}
        self.all_Names_list = []
        # Beispiel-Daten für das Inhaltsverzeichnis
        self.content_dict = {}
        self.content_dict["New_topic"] = ["New_topic", "New_topic"]
        
        for key, value in self.format_vorlage.items():
            self.all_sectors[key] = OpenExcel(os.path.join(self.aktiv_folder, key+".csv"), ["Name"], value)
            for name in self.all_sectors[key].get_collumns_list("Name"): #Gets all the names from the csv files
                str_name = self.convert_to_plain_text(name)
                self.all_Names_list.append(str_name)
                
                #Make the content with a short description of the topic
                name_row = self.all_sectors[key].get_row_elements_by_name(name)
                self.content_dict[str_name] = [str(self.convert_to_plain_text(list(name_row.values())[1])), name]#The key = name_plain_text, the value = [short description, name]; name is the name which you can search in the csv file.
        
        print(self.content_dict)
        
            #print(self.all_sectors[key].get_collumns_list("Name"))
        self.all_Names_list = set(self.all_Names_list)#Remove all the duplicates
        #Remove all the non string values from the list
        for v in self.all_Names_list:
            if type(v) != str:
                self.all_Names_list.remove(v)
                
        
                
        print("Format_vorlage:"+str(self.format_vorlage))
        print("All_Names:"+str(self.all_Names_list))
        
        
    def update_content_dict(self, name_plain_text, list_info):
        #This method updates the content_dict with the new names
        #self.all_Names_list = []
        self.content_dict[name_plain_text] = list_info
        self.table_of_content.update_table(self.content_dict)
        
    
    def open_info_js(self, folder_path):
        '''This method opens a json file and returns the data.
        Data contains the self.format_vorlage of all the csv files in this folder.
        Also there can be other data in the json file.
        
        The name of the json file is _folder_data.json'''
        path = os.path.join(folder_path, "_folder_data.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    
    def convert_to_plain_text(self, text):
        # Überprüfen, ob der Text HTML-Formatierung aufweist
        if "<html" in text.lower() or "<body" in text.lower():
            # HTML in reinen Text umwandeln
            doc = QTextDocument()
            doc.setHtml(text)
            plain_text = doc.toPlainText()
            return plain_text
        else:
            # Text hat kein HTML, daher unverändert zurückgeben
            return text
    
    def show_available_data(self):
        '''This method shows the available data from the self.all_sectors. 
        If there arent any data, it shows just the predefined format and makes a new data.'''
        input_topic = self.input1.text()
        # Leere die Eingabe
        self.clear_uinputs()
        # Überprüfe, ob der Name schon in der self.all_names_list vorhanden ist
        if input_topic in self.all_Names_list:
            # Wenn der Name vorhanden ist, zeige die Daten an
            self.change_topic(input_topic)
            
        else:
            # Wenn der Name nicht vorhanden ist, zeig eine leere Eingabe an
            self.clear_uinputs()
    
    def change_show_topic(self, row, column):
        '''This method change the topic and shows the available data.
        Also if the topic Name is ^New Flashcard^ it creates a new topic and shows the available data.'''
        #print("Row %d and Column %d was clicked" % (row, column))
        #print(self.content[row][0])
        topic = list(self.content_dict.keys())[row]
        info_list = self.content_dict[topic]
        real_name = info_list[1]
        if topic == "New_topic":
            topic = self.create_new_topic()
        else:
            if not self.editor_bool:
                self.input1.setText(real_name)
            else:
                self.input1.setHtml(real_name)
            self.change_topic(real_name)
            
    def create_new_topic(self):
        '''This method creates a new topic and returns the name of the new topic.'''
        #print("New Topic")
        #clear the inputs of the input1
        if not self.editor_bool:
            self.input1.setText("")
        else:
            self.input1.setHtml("")
        #Put the curser in the input1
        self.input1.setFocus()
        # Wenn der Name nicht vorhanden ist, zeig eine leere Eingabe an
        self.clear_uinputs()
    
    def clear_uinputs(self):
        '''This method clears all the inputs of the self.inputs_form. Without the input1'''
        for key, value in self.inputs_form.items():
            for key2, value2 in value.items():
                if not self.editor_bool:
                    value2.setText("")
                else:
                    value2.setHtml("")
        
    def change_topic(self, topic):
        '''This method changes the topic of all the editors and shows the available data.
        It just fills the self.inputs_form with the data from the self.all_sectors'''
        #Sucht die Daten in der Excel Tabelle vom self.all_sectors
        full_data_of_name = {}
        for key, value in self.all_sectors.items():
            row = value.get_row_elements_by_name(topic)#Here i get a dictionary
            if row == None:
                continue
            full_data_of_name[key] = row
            #print(key)
            print(row)
            #print(self.inputs_form)
            #look if the keys are in the self.inputs_form and if yes, then put the data in the input
            for key2, value2 in row.items():
                if key2 in self.inputs_form[key].keys():
                    if not self.editor_bool:
                        #print(value2)
                        if str == type(value2):#check if the value is a string and not a nan
                            self.inputs_form[key][key2].setText(value2)
                    else:
                        print("set html")
                        self.inputs_form[key][key2].setHtml(value2)#isn't in use now
        print(full_data_of_name)
    
    
    def input1_text_changed(self):
        text_input1 = self.input1.text()
        # Wenn der Benutzer die Tab-Taste drückt, wird der nächste beste Vorschlag angezeigt
        if "\t" in text_input1:
            self.input1.setText(self.get_next_suggestion(text_input1.replace("\t", "")))
        else:
            # Vorschlagslabel aktualisieren
            self.show_suggestion(text_input1)
                 
    def show_suggestion(self, text):
        # Nächsten besten Vorschlag finden
        next_suggestion = self.get_next_suggestion(text.lower())
        # Vorschlagslabel aktualisieren
        self.suggestion_label.setText(next_suggestion)
        
    def get_next_suggestion(self, text):
        # Vorschläge filtern, die mit der Eingabe beginnen (in Kleinbuchstaben)
        matches = [s for s in self.all_Names_list if str(s).lower().startswith(text)]


        # Nächsten besten Vorschlag auswählen
        if matches:
            return matches[0]
        else:
            return ""
        
    def get_lineedit_text_dict(self, lineedit_dict):
        text_dict = {}
        if not self.editor_bool:
            for key, value in lineedit_dict.items():
                text_dict[key] = value.text()
        else:
            for key, value in lineedit_dict.items():
                text_dict[key] = value.toHtml()
        return text_dict
        
    def save_the_inputs(self):
        #Schaut zuersto ob es ein HTML Editor oder ein Plain Text Editor ist
        if not self.editor_bool:
            input1_text = str(self.input1.text())
            print(input1_text)
            if input1_text.isspace() or input1_text == "":
                Exception("Name darf nicht leer sein")
                print("Name darf nicht leer sein")
                return
        else:
            input1_text = str(self.input1.toHtml())
            text = self.convert_to_plain_text(input1_text)
            if input1_text.isspace() or input1_text == "":
                Exception("Name darf nicht leer sein")
                print("Name darf nicht leer sein")
                return
        
        # Speichere die Eingaben in eine Excel Datei ab
        for key, value in self.all_sectors.items():
            if not self.editor_bool:
                #self.all_Names_list.append(input1_text)
                self.all_sectors[key].add_data_to_df(input1_text, self.get_lineedit_text_dict(self.inputs_form[key]))
            else:                
                #self.all_Names_list.append(input1_text)
                self.all_sectors[key].add_data_to_df(input1_text, self.get_lineedit_text_dict(self.inputs_form[key]))
            self.all_sectors[key].save_df()
        print("Eingaben gespeichert")
        self.update_content_dict(self.convert_to_plain_text(input1_text), [list(self.get_lineedit_text_dict(self.inputs_form[key]).values())[0], input1_text])
        print("Alles neu geladen")
    
    def clear_the_inputs(self):
        # Leere die Eingabe
        for key, value in self.inputs_form.items():
            for key2, value2 in value.items():
                if not self.editor_bool:
                    value2.setText("")
                else:
                    value2.setHtml("")
        if not self.editor_bool:
            self.input1.setText("")
        else:
            self.input1.setHtml("")     
        
    
    def read_inputs(self):
        # Lese die Eingaben aus
        print(self.inputs_form)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    verbs_con_directory = r"_Data_Col\Franz\Verbs\conjugate"
    os.makedirs(verbs_con_directory, exist_ok=True)
    format_vorlage = {"Antwort":["Abschnitt 1", "Test"]}
    
    
    main_window = MainWindow(verbs_con_directory, editor = False)
    sys.exit(app.exec_())
