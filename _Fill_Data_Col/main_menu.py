import sys
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QComboBox, QGroupBox, \
    QHBoxLayout, QRadioButton, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QPlainTextEdit, QTextEdit, \
    QScrollArea, QScrollBar, QShortcut, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QScrollArea, \
    QSizePolicy, QCheckBox

from qt5_tools import SearchInput, DictionaryTree, DictionaryTree_Folder, DictionaryTree_select
import main_diverse
import main_learn2
from bibly_lib import BibliAssistant as bibli

class MainWindow(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()
        self.setWindowTitle("Bibliothek Assistant")
        self.setGeometry(100, 100, 400, 300)

        # Datas
        self.folder_path = folder_path
        self.bibli_as = bibli(folder_path)
        self.all_themes = []
        self.format_vorlage = {"present_list":["je","tu", "il"]}
        
        
        
        # Hauptwidget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Hauptlayout
        main_layout = QVBoxLayout(main_widget)

        # Dropdown
        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)
        
        def change_aktive_subject():
            self.bibli_as.change_aktive_subject(dropdown.currentText())
            #Get new options
            self.actualice_options(self.bibli_as.aktive_subject_folder, self.bibli_as.aktive_subject_folder)
            self.actualice_selection(self.bibli_as.aktive_subject_folder, self.bibli_as.aktive_subject_folder)
            print(self.selected_folder_path)
            print(self.bibli_as.aktive_subject_folder)
        
        dropdown = QComboBox()
        dropdown.addItems(self.bibli_as.all_subjects)
        dropdown.setCurrentText(self.bibli_as.aktive_subject)
        #Whene dropdown is changed, the function actualice_options is called
        dropdown.currentTextChanged.connect(change_aktive_subject)
        horizontal_layout.addWidget(dropdown, alignment=Qt.AlignCenter)
        
        spacer = QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)# Horizontaler Spacer separating the dropdown from the tab widget
        main_layout.addItem(spacer)
        
        # Tab Widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Search Bereich///////////////////////////////
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        self.search_input = SearchInput(self.all_themes)#all themes should come from the bibly lib
        self.search_input.setPlaceholderText("Suche...")
        self.search_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.search_input.setMinimumWidth(int(self.width() * 0.9))  # Setze die Mindestbreite auf 90% der Fensterbreite
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input, alignment=Qt.AlignCenter)
        
        # Options to chose if you wana connect the Word app, to make search about the selected words.
        # Make two Checkboxes
        permissions_group = QGroupBox("Permissions")
        horizontal_group = QHBoxLayout(permissions_group)
        self.Auto_search_box = QCheckBox("Auto Seach")
        self.Permision_box = QCheckBox("Premission to read")
        self.Auto_search_box.setChecked(True)
        self.Permision_box.setChecked(True)
        horizontal_group.addWidget(self.Auto_search_box)
        horizontal_group.addWidget(self.Permision_box)
        search_layout.addWidget(permissions_group)
        
        
        
        # # Spacer
        # search_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        radio_group = QGroupBox("Search Engine")
        radio_layout = QHBoxLayout(radio_group)
        self.radio_button1 = QRadioButton("Wiki")
        self.radio_button2 = QRadioButton("Google")
        self.radio_button3 = QRadioButton("Bibli")
        self.radio_button3.setChecked(True)  # Aktiviere den ersten Radio-Button
        radio_layout.addWidget(self.radio_button1)
        radio_layout.addWidget(self.radio_button2)
        radio_layout.addWidget(self.radio_button3)
        search_layout.addWidget(radio_group)
        # Spacer
        search_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        #Text Editor
        self.text_editor = QTextEdit()
        search_layout.addWidget(self.text_editor)
        
        tab_widget.addTab(search_tab, "Search")#Add the tab to the tab widget

        #Specials Widgets or Zusätze
        #self.Word_ap_con = Word_aplication_con()
        #self.Word_ap_con.connect(lambda x: print(x), polling_interval=1)




        # Learn Bereich///////////////////////////////
        learn_tab = QWidget()
        learn_layout = QVBoxLayout(learn_tab)
        
        self.dir_label_sel = QLabel(self)
        self.dir_label_sel.setStyleSheet("font-weight: bold;")
        learn_layout.addWidget(self.dir_label_sel)
        
        self.treeWidget_Folder_sel = DictionaryTree_Folder(self, self.bibli_as.aktive_subject_folder, False)
        self.bibli_as.on_subject_change(self.treeWidget_Folder_sel.change_folder_path)#Ruft diese Funktion auf, wenn sich das aktive Thema und somit ach der Path für den Ordner geänder wird und übermittelt gleich das Argument.
        learn_layout.addWidget(self.treeWidget_Folder_sel)
        
        self.treeWidget_theme_select = DictionaryTree_select(self, self.format_vorlage)
        learn_layout.addWidget(self.treeWidget_theme_select)
        # Button to star the fill process programm
        button_learn = QPushButton("Start", self)
        button_learn.clicked.connect(self.start_learn_bibli)
        learn_layout.addWidget(button_learn)
        tab_widget.addTab(learn_tab, "Learn")
        
        
        
        # Fill Bereich///////////////////////////////
        fill_tab = QWidget()
        fill_layout = QVBoxLayout(fill_tab)
        
        self.dir_label = QLabel(self)
        self.dir_label.setStyleSheet("font-weight: bold;")
        fill_layout.addWidget(self.dir_label)
        
        self.treeWidget_folder_edit_sel = DictionaryTree_Folder(self, self.bibli_as.aktive_subject_folder)
        self.bibli_as.on_subject_change(self.treeWidget_folder_edit_sel.change_folder_path)#Ruft diese Funktion auf, wenn sich das aktive Thema und somit ach der Path für den Ordner geänder wird und übermittelt gleich das Argument.
        fill_layout.addWidget(self.treeWidget_folder_edit_sel)
        
        # Format Vorlage Optionen
        self.format_opt = DictionaryTree(self.format_vorlage)
        fill_layout.addWidget(self.format_opt)
        
        # Make two Checkboxes
        self.checkBox1 = QCheckBox("Grosser Editor")
        self.checkBox2 = QCheckBox("Format Vorlage Speichern")
        self.checkBox1.setChecked(True)
        self.checkBox2.setChecked(True)
        fill_layout.addWidget(self.checkBox1)
        fill_layout.addWidget(self.checkBox2)
        
        # Button to star the fill process programm
        button = QPushButton("Start", self)
        button.clicked.connect(self.start_fill_bibli)
        fill_layout.addWidget(button)
        tab_widget.addTab(fill_tab, "Fill")




        # Summary Bereich///////////////////////////////
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        summary_dropdown = QComboBox()
        summary_dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        summary_layout.addWidget(summary_dropdown)
        tab_widget.addTab(summary_tab, "Summary")
        
        # Reading Bereich///////////////////////////////
        read_tab = QWidget()
        read_layout = QVBoxLayout(read_tab)
        
        #read_layout.addWidget(summary_dropdown)
        tab_widget.addTab(summary_tab, "Reading")

        self.show()
    
    def search_the_input(self, input):
        #Checking the searching options
        print("search_the_input")
        #Which search engine is selected
        if self.radio_button1.isChecked():#Wiki search
            self.text_editor.setText(str(result))
        elif self.radio_button2.isChecked():#Google search
            pass
        elif self.radio_button3.isChecked():#Bibli search
            result = self.bibli_as.search_names_in_folder(input)
            text_result = ""
            for res, path in result.items():
                text_result += str(res) + "\n"
                for info in path:
                    text_result += str(info) + "\n"
                text_result += "\n"
            self.text_editor.setText(str(text_result))
    
    def search(self):
        result = self.bibli_as.search_names_in_folder(self.search_input.text())
        text_result = ""
        for res, path in result.items():
            text_result += str(res) + "\n"
            for info in path:
                text_result += str(info) + "\n"
            text_result += "\n"
        self.text_editor.setText(str(text_result))
        
    def actualice_options(self, selected_folder_name, selected_folder_path):
        self.dir_label.setText(str(selected_folder_path))
        self.selected_folder_path = selected_folder_path
        #Check if there is a format_vorlage.json file in the folder
        path = os.path.join(self.selected_folder_path, "_folder_data.json")
        if os.path.isfile(path):
            with open(path, "r") as f:
                self.format_vorlage = json.load(f)
        else:
            self.format_vorlage = {"Antwort":["Kurz:","Genaue Beschreibung"]}
        self.bibli_as.set_active_folder_of_active_subject(self.selected_folder_path)
        self.format_opt.update_dict(self.format_vorlage)
        print(self.format_vorlage)
    
    def actualice_selection(self, selected_folder_name, selected_folder_path):
        self.dir_label_sel.setText(str(selected_folder_path))
        self.selected_folder_path = selected_folder_path
        #Check if there is a format_vorlage.json file in the folder
        path = os.path.join(self.selected_folder_path, "_folder_data.json")
        if os.path.isfile(path):
            with open(path, "r") as f:
                self.format_vorlage = json.load(f)
        else:
            self.format_vorlage = {}
        self.bibli_as.set_active_folder_of_active_subject(self.selected_folder_path)
        self.treeWidget_theme_select.update_dict(self.format_vorlage)
        print(self.format_vorlage)
        
        
    def start_fill_bibli(self):
        print("Start the fill process")
        self.format_vorlage = self.format_opt.get_dict()
        if self.checkBox2.isChecked():
            #save the format_vorlage in the options of the folder
            path = os.path.join(self.selected_folder_path, "_folder_data.json")
            with open(path, "w") as f:
                json.dump(self.format_vorlage, f)
        os.makedirs(self.selected_folder_path, exist_ok=True)
        self.fill_window = main_diverse.MainWindow(self.selected_folder_path, editor = self.checkBox1.isChecked(), format_vorlage=self.format_vorlage)
                
    def start_learn_bibli(self):
        print("Start the learn process")
        #Check if the format_vorlage is empty
        if self.format_vorlage == {}:
            QMessageBox.about(self, "Error", "There is no format_vorlage in the folder")
            return
        else:
            print("Selected Forlage:",self.format_vorlage)
            print("Selected Path:", self.selected_folder_path)
            self.learn_window = main_learn2.MyWindow(self.selected_folder_path, self.format_vorlage)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    path_folder = r"_Data_Col"
    window = MainWindow(path_folder)
    sys.exit(app.exec_())
