import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QScrollArea, QFormLayout
from PyQt5 import QtCore
import json
import make_quest_lib as mql
import os

sys.path.append("_Fill_Data_Col")

from save_exc_lib import OpenExcel

class MyWindow(QWidget):
    # benutzerdefiniertes Signal definieren
    closed = QtCore.pyqtSignal()

    def __init__(self, folder_path, sel_format):
        super().__init__()
        self.sel_format = sel_format#In dieser Struktur wird abgefragt
        self.aktiv_folder = folder_path
        #open the _folder_data.json file whith the data about the full format
        self.full_format_vorlage = self.open_info_js(self.aktiv_folder)
        
        data_manager = {"path": folder_path}
        for key, value in self.full_format_vorlage.items():
            #print(key, value)
            self.verben_present = OpenExcel(os.path.join(self.aktiv_folder, key+".csv"), ["Name"], value)
            data_manager[key] = self.verben_present
        #==> data_manager = {"path": folder_path, "present":self.verben_present, "imparfait":self.verben_imparfait, "passe_compose":self.verben_passe_compose, "future":self.verben_future, "subjonctif_present":self.verben_subjonctif_present, "conditionnel_present":self.verben_conditionnel_present, "gerondif":self.verben_gerondif}
        
        self.teacher_asker = mql.quest_answ(data_manager, self.sel_format)
        self.teacher_asker.set_sel_format(self.sel_format)#give it the selected format, so how i want to learn.
        #For Example: self.sel_format = {"present":["je", "tu", "il", "nous", "vous", "ils"], "imparfait":["je", "tu", "il", "nous", "vous", "ils"], "gerondif":["je", "tu", "il", "nous", "vous", "ils"], "future1":["je", "tu", "il", "nous", "vous", "ils"],"conditionnel_present":["je", "tu", "il", "nous", "vous", "ils"], "subjonctif_present":["je", "tu", "il", "nous", "vous", "ils"], "passe_compose":["je", "tu", "il", "nous", "vous", "ils"]}
        self.act_verb_name, self.format_vorlage = self.teacher_asker.make_new_quest()
        
        self.solution = ""
        
        
        # Erstelle ein vertikales Layout
        layout = QVBoxLayout()
        
        # Button erstellen für das Öffnen des zweiten Fensters
        self.button = QPushButton('Options')
        # Erstelle einen Button
        layout.addWidget(self.button)
        # Zweites Fenster als Instanzvariable erstellen
        self.second_window = None
        self.third_window = None
        # Button-Klick-Event verknüpfen
        self.button.clicked.connect(self.open_options)
        
        
        layout.addWidget(QLabel("Verb:"+self.act_verb_name))        

        # Erstelle eine srollierbaren Bereich mit inputs und labels
        # ScrollWidget erstellen
        scrollWidget = QWidget()
        scrollWidgetLayout = QVBoxLayout(scrollWidget)
        self.inputs_form = {}
        
        for key, value in self.format_vorlage.items():
            input_abs = {}
            #Untertitel == Abschnitstitel
            scrollWidgetLayout.addWidget(QLabel(key+":"))
            
            #Abs_layout = QFormLayout()
            for lable in value:
                # Erstelle ein Formular-Layout für den Abschnitt "Texteingabe"
                input_text = QLineEdit()
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
        
        # Erstelle einen Button
        button = QPushButton("Eingaben auswerten")
        layout.addWidget(button)
        # Verbinde das clicked-Signal des Buttons mit der Methode read_inputs
        button.clicked.connect(self.check_answer,)

        # Setze das Layout des Fensters
        self.setLayout(layout)
        # Setze den Fenstertitel und zeige das Fenster an
        self.setWindowTitle("Verben Editor")
        self.show()
    
    def open_info_js(self, folder_path):
        '''This method opens a json file and returns the data.
        Data contains the self.format_vorlage of all the csv files in this folder.
        Also there can be other data in the json file.
        
        The name of the json file is _folder_data.json'''
        path = os.path.join(folder_path, "_folder_data.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    
    def update_format_vorlage(self):
        
        # Entferne den alten ersten QLabel
        old_scroll_area = self.layout().itemAt(1).widget()
        self.layout().removeWidget(old_scroll_area)
        old_scroll_area.setParent(None)
        # Erstelle einen neuen QLabel mit dem neuen Text
        new_label = QLabel("Verb:"+self.act_verb_name)
        
        self.layout().insertWidget(1, new_label)
        
        # Entferne den alten Scrollbereich
        old_scroll_area = self.layout().itemAt(2).widget()
        self.layout().removeWidget(old_scroll_area)
        old_scroll_area.setParent(None)

        
        
        
        # Erstelle einen neuen Scrollbereich mit den aktualisierten Inputs
        scrollWidget = QWidget()
        scrollWidgetLayout = QVBoxLayout(scrollWidget)
        self.inputs_form = {}

        for key, value in self.format_vorlage.items():
            input_abs = {}
            # Untertitel == Abschnitstitel
            scrollWidgetLayout.addWidget(QLabel(key+":"))

            for label in value:
                # Erstelle ein Formular-Layout für den Abschnitt "Texteingabe"
                input_text = QLineEdit()
                # create a horizontal layout for each row
                row_layout = QHBoxLayout()
                #scrollWidgetLayout.addRow(QLabel(lable), input_text)
                row_layout.addWidget(QLabel(label))
                row_layout.addWidget(input_text)
                scrollWidgetLayout.addLayout(row_layout)
                input_abs[label]=input_text
            self.inputs_form[key] = input_abs
            # Füge einen Abstand von 10 Pixeln hinzu
            scrollWidgetLayout.addSpacing(20)

        # Scrollbereich erstellen
        new_scroll_area = QScrollArea()
        new_scroll_area.setWidgetResizable(True)
        new_scroll_area.setWidget(scrollWidget)

        # Füge den neuen Scrollbereich hinzu
        
        self.layout().insertWidget(2, new_scroll_area)

        
    def get_lineedit_text_dict(self, lineedit_dict):
        text_dict = {}
        for key, value in lineedit_dict.items():
            text_dict[key] = value.text()
        return text_dict
    
    def show_new_quest(self):
        self.act_verb_name, self.format_vorlage = self.teacher_asker.make_new_quest()
        self.update_format_vorlage()
        self.close_third_window()
    
    def check_answer(self):
        # Erstelle ein Dict mit allen eingegebenen Texten
        input_text_dict = {}
        for key, value in self.inputs_form.items():
            input_text_dict[key] = self.get_lineedit_text_dict(value)
        #print(input_text_dict)
        self.response, self.solution = self.teacher_asker.check_answ(self.act_verb_name, input_text_dict)
        #print(self.replace_inputs_with_solution(solution))
        #print("solution:",self.solution)
        self.show_solution()
        
        
    def show_solution(self):
        # Überprüfen, ob das zweite Fenster bereits erstellt wurde
        if self.third_window is None:
            # Neues Fenster erstellen
            self.third_window = QWidget()
            self.third_window.setGeometry(100, 100, 400, 300)
            self.third_window.setWindowTitle('Drittes Fenster')

            layout = QVBoxLayout(self.third_window) # create a QVBoxLayout object

            label = QLabel()
            text = ""
            for key, value in self.solution.items():
                text += f"{key}\n"
                for key2, value2 in value.items():
                    text += f"    {key2}: {value2}\n"
                text += "\n"
            label.setText(text)

            layout.addWidget(label) # add the label to the layout
            # Create a button widget
            button = QPushButton('Next Question', self.third_window)
            button.clicked.connect(self.show_new_quest) # connect button to close the window

            layout.addWidget(button) # add the button to the layout

            # Signal verknüpfen, um self.second_window wieder auf None zu setzen
            self.third_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.third_window.destroyed.connect(self.set_third_window_to_none)

            self.third_window.show() # show the window

    def close_third_window(self):
        self.third_window.close()
    
    def open_options(self):
        # Überprüfen, ob das zweite Fenster bereits erstellt wurde
        if self.second_window is None:
            # Neues Fenster erstellen
            self.second_window = QWidget()
            self.second_window.setGeometry(100, 100, 400, 300)
            self.second_window.setWindowTitle('Zweites Fenster')

            # Label für den Text erstellen und in das zweite Fenster einfügen
            text_label = QLabel('Dein eingegebener Text: ', self.second_window)
            text_label.move(20, 20)

            # Zweites Fenster anzeigen
            self.second_window.show()

            # Signal verknüpfen, um self.second_window wieder auf None zu setzen
            self.second_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.second_window.destroyed.connect(self.set_second_window_to_none)

    def set_second_window_to_none(self):
        self.second_window = None
        # ausgelöstes Signal emitieren
        self.closed.emit()
    
    def set_third_window_to_none(self):
        self.third_window = None
        # ausgelöstes Signal emitieren
        self.closed.emit()

    def closeEvent(self, event):
        # Überprüfen, ob das zweite Fenster existiert
        if self.second_window is not None:
            self.second_window.close()

        # Standard-Implementierung von closeEvent() aufrufen
        super().closeEvent(event)


if __name__ == '__main__':
    # Qt-Anwendung initialisieren und Fenster anzeigen
    verbs_con_directory = r"_Data_Col\Franz\Verbs\conjugate"
    sel_format = {"present":["tu", "il", "nous", "vous", "ils"], "imparfait":["je", "tu", "vous", "ils"]}
    app = QApplication(sys.argv)
    window = MyWindow(verbs_con_directory, sel_format)
    sys.exit(app.exec_())
