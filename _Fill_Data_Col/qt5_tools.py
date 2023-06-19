from PyQt5 import QtWidgets, QtCore
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem, QInputDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
#Für die Lerneintellungen
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid

class SearchInput(QtWidgets.QLineEdit):
    def __init__(self, suggestions):
        super().__init__()
        self.suggestions = suggestions
        self.completer = QtWidgets.QCompleter(self.suggestions, self)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)  # Filtermodus anpassen
        self.setCompleter(self.completer)

class TableOfContents(QWidget):
    """Creates a table of contents widget. The content_dict must be a dictionary
    with the following structure: {'topic': {'function': function, 'info': '...'}, ...}
    If you want to add a function to the table of contents: the use this:
    table.cellClicked.connect(funktion with the Parameter (row, column))"""
    def __init__(self, content_dict):
        super().__init__()
        self.content_dict = content_dict
        self.mlayout = QVBoxLayout()
        self.table = QTableWidget()
        self.init_ui()

    def init_ui(self):
        self.table.setColumnCount(1)
        self.table.setRowCount(len(self.content_dict))

        # Hide table header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.hide()

        # Create table of contents
        row = 0
        for topic, info in self.content_dict.items():
            item = QTableWidgetItem(topic)
            self.table.setItem(row, 0, item)
            row += 1

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)#Not editable
        self.mlayout.addWidget(self.table)
        self.setLayout(self.mlayout)

    def handle_cell_clicked(self, row, column):
        topic = list(self.content_dict.keys())[row]
        info = self.content_dict[topic]
        info['function']()

    def sizeHint(self):
        return self.table.sizeHint()
    
    def update_table(self, content_dict):
        self.content_dict = content_dict
        self.table.clear()
        self.table.setRowCount(len(self.content_dict))
        row = 0
        for topic, info in self.content_dict.items():
            item = QTableWidgetItem(topic)
            self.table.setItem(row, 0, item)
            row += 1




class TextEdit(QTextEdit):
    
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.obj_parent = parent
        print(self.obj_parent)
        # Setup the QTextEdit
        self.setAutoFormatting(QTextEdit.AutoAll)
        self.setAcceptRichText(True)
        self.setTabStopWidth(25)
        self.setUndoRedoEnabled(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setWordWrapMode(QTextOption.WordWrap)
        self.setAcceptDrops(True)
        self.selectionChanged.connect(self.set_parents_active_editor)
        # Connect signals and slots
        #self.cursorPositionChanged.connect(self.update_format)
        # Initialize default font size.
        font = QFont('Times', 12)
        self.setFont(font)
        # We need to repeat the size to init the current format.
        self.setFontPointSize(12)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None
        
        self.FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        self.IMAGE_EXTENSIONS = ['.jpg','.png','.bmp']
        self.HTML_EXTENSIONS = ['.htm', '.html']

    def connect_formatbar(self, obj):
        self.FormatBar_obj = obj
        
    def set_parents_active_editor(self):
        self.FormatBar_obj.active_editor = self
        self.update_format()
        
    def hexuuid(self):
        return uuid.uuid4().hex

    def splitext(self, p):
        return os.path.splitext(p)[1].lower()

    
    def canInsertFromMimeData(self, source):

        if source.hasImage():
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        
        cursor = self.textCursor()
        document = self.document()

        
        
        if source.hasUrls():

            for u in source.urls():
                file_ext = self.splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in self.IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QtGui.QTextDocument.ResourceType.ImageResource.value, u, image)
                    cursor.insertImage(u.toLocalFile())

                else:
                    # If we hit a non-image or non-local URL break the loop and fall out
                    # to the super call & let Qt handle it
                    break

            else:
                # If all were valid images, finish here.
                return
        
        elif source.hasText():
            cursor = self.textCursor()
            cursor.insertText(source.text())


        elif source.hasImage():
            image = source.imageData()
            uuid = self.hexuuid()
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            return


        
        
        print(source)

        
        super(TextEdit, self).insertFromMimeData(source)


    
    #Everything in connection with the Formatbar
    def block_signals(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def update_format(self):
        """
        Update the font format toolbar/actions when a new text selection is made. This is neccessary to keep
        toolbars/etc. in sync with the current edit state.
        :return:
        """
        # Disable signals for all format widgets, so changing values here does not trigger further formatting.
        self.block_signals(self.FormatBar_obj._format_actions, True)

        self.FormatBar_obj.fonts.setCurrentFont(self.currentFont())
        # Nasty, but we get the font-size as a float but want it was an int
        self.FormatBar_obj.fontsize.setCurrentText(str(int(self.fontPointSize())))

        self.FormatBar_obj.italic_action.setChecked(self.fontItalic())
        self.FormatBar_obj.underline_action.setChecked(self.fontUnderline())
        self.FormatBar_obj.bold_action.setChecked(self.fontWeight() == QFont.Bold)

        self.FormatBar_obj.alignl_action.setChecked(self.alignment() == Qt.AlignLeft)
        self.FormatBar_obj.alignc_action.setChecked(self.alignment() == Qt.AlignCenter)
        self.FormatBar_obj.alignr_action.setChecked(self.alignment() == Qt.AlignRight)
        self.FormatBar_obj.alignj_action.setChecked(self.alignment() == Qt.AlignJustify)

        self.block_signals(self.FormatBar_obj._format_actions, False)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        try:
            with open(path, 'rU') as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            # Qt will automatically try and guess the format as txt/html
            self.setText(text)
            self.update_title()

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        text = self.toHtml() if self.splitext(self.path) in self.HTML_EXTENSIONS else self.toPlainText()

        try:
            with open(self.path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        text = self.toHtml() if self.splitext(path) in self.HTML_EXTENSIONS else self.toPlainText()

        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle("%s - Megasolid Idiom" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.setLineWrapMode( 1 if self.lineWrapMode() == 0 else 0 )


class FormatBar():
    def __init__(self, parent=None):
        self.obj = parent
        
        #Connect the Formatbar to the TextEdits
        for edit in self.obj.all_editors:
            edit.connect_formatbar(self.obj)
        
        status_bar = QStatusBar()
        self.obj.setStatusBar(status_bar)
        
        FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        IMAGE_EXTENSIONS = ['.jpg','.png','.bmp']
        HTML_EXTENSIONS = ['.htm', '.html']

        def hexuuid():
            return uuid.uuid4().hex

        def splitext(p):
            return os.path.splitext(p)[1].lower()
        

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        # file_toolbar = QToolBar("File")
        # file_toolbar.setIconSize(QSize(14, 14))
        # self.addToolBar(file_toolbar)
        # file_menu = self.menuBar().addMenu("&File")


        # saveas_file_action = QAction(QIcon(os.path.join(path_to_images_icones, 'disk--pencil.png')), "Save As...", self)
        # saveas_file_action.setStatusTip("Save current page to specified file")
        # saveas_file_action.triggered.connect(self.file_saveas)
        # file_menu.addAction(saveas_file_action)
        # file_toolbar.addAction(saveas_file_action)

        # print_action = QAction(QIcon(os.path.join(path_to_images_icones, 'printer.png')), "Print...", self)
        # print_action.setStatusTip("Print current page")
        # print_action.triggered.connect(self.file_print)
        # file_menu.addAction(print_action)
        # file_toolbar.addAction(print_action)

        path_to_images_icones = r"_Fill_Data_Col\images"
        
        
        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.obj.addToolBar(edit_toolbar)
        edit_menu = self.obj.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join(path_to_images_icones, 'arrow-curve-180-left.png')), "Undo", self.obj)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(lambda: self.obj.active_editor.undo())
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join(path_to_images_icones, 'arrow-curve.png')), "Redo", self.obj)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(lambda: self.obj.active_editor.redo())
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join(path_to_images_icones, 'scissors.png')), "Cut", self.obj)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(lambda: self.obj.active_editor.cut())
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join(path_to_images_icones, 'document-copy.png')), "Copy", self.obj)
        copy_action.setStatusTip("Copy selected text")
        cut_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(lambda: self.obj.active_editor.copy())
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join(path_to_images_icones, 'clipboard-paste-document-text.png')), "Paste", self.obj)
        paste_action.setStatusTip("Paste from clipboard")
        cut_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(lambda: self.obj.active_editor.paste())
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join(path_to_images_icones, 'selection-input.png')), "Select all", self.obj)
        select_action.setStatusTip("Select all text")
        cut_action.setShortcut(QKeySequence.SelectAll)
        select_action.triggered.connect(lambda: self.obj.active_editor.selectAll())
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(QIcon(os.path.join(path_to_images_icones, 'arrow-continue.png')), "Wrap text to window", self.obj)
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(lambda: self.obj.active_editor.edit_toggle_wrap())
        edit_menu.addAction(wrap_action)

        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(16, 16))
        self.obj.addToolBar(format_toolbar)
        format_menu = self.obj.menuBar().addMenu("&Format")

        # We need references to these actions/settings to update as selection changes, so attach to self.obj.
        self.obj.fonts = QFontComboBox()
        self.obj.fonts.currentFontChanged.connect(lambda f: self.obj.active_editor.setCurrentFont(f))
        format_toolbar.addWidget(self.obj.fonts)

        self.obj.fontsize = QComboBox()
        self.obj.fontsize.addItems([str(s) for s in FONT_SIZES])

        # Connect to the signal producing the text of the current selection. Convert the string to float
        # and set as the pointsize. We could also use the index + retrieve from FONT_SIZES.
        self.obj.fontsize.currentIndexChanged[str].connect(lambda s: self.obj.active_editor.setFontPointSize(float(s)))
        format_toolbar.addWidget(self.obj.fontsize)

        self.obj.bold_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-bold.png')), "Bold", self.obj)
        self.obj.bold_action.setStatusTip("Bold")
        self.obj.bold_action.setShortcut(QKeySequence.Bold)
        self.obj.bold_action.setCheckable(True)
        self.obj.bold_action.toggled.connect(lambda x: self.obj.active_editor.setFontWeight(QFont.Bold if x else QFont.Normal))
        format_toolbar.addAction(self.obj.bold_action)
        format_menu.addAction(self.obj.bold_action)

        self.obj.italic_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-italic.png')), "Italic", self.obj)
        self.obj.italic_action.setStatusTip("Italic")
        self.obj.italic_action.setShortcut(QKeySequence.Italic)
        self.obj.italic_action.setCheckable(True)
        self.obj.italic_action.toggled.connect(lambda x: self.obj.active_editor.setFontItalic(QFont.StyleItalic if x else QFont.StyleNormal))
        format_toolbar.addAction(self.obj.italic_action)
        format_menu.addAction(self.obj.italic_action)

        self.obj.underline_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-underline.png')), "Underline", self.obj)
        self.obj.underline_action.setStatusTip("Underline")
        self.obj.underline_action.setShortcut(QKeySequence.Underline)
        self.obj.underline_action.setCheckable(True)
        self.obj.underline_action.toggled.connect(lambda x: self.obj.active_editor.setFontUnderline(True if x else False))
        format_toolbar.addAction(self.obj.underline_action)
        format_menu.addAction(self.obj.underline_action)

        format_menu.addSeparator()

        self.obj.alignl_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-alignment.png')), "Align left", self.obj)
        self.obj.alignl_action.setStatusTip("Align text left")
        self.obj.alignl_action.setCheckable(True)
        self.obj.alignl_action.triggered.connect(lambda: self.obj.active_editor.setAlignment(Qt.AlignLeft))
        format_toolbar.addAction(self.obj.alignl_action)
        format_menu.addAction(self.obj.alignl_action)

        self.obj.alignc_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-alignment-center.png')), "Align center", self.obj)
        self.obj.alignc_action.setStatusTip("Align text center")
        self.obj.alignc_action.setCheckable(True)
        self.obj.alignc_action.triggered.connect(lambda: self.obj.active_editor.setAlignment(Qt.AlignCenter))
        format_toolbar.addAction(self.obj.alignc_action)
        format_menu.addAction(self.obj.alignc_action)

        self.obj.alignr_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-alignment-right.png')), "Align right", self.obj)
        self.obj.alignr_action.setStatusTip("Align text right")
        self.obj.alignr_action.setCheckable(True)
        self.obj.alignr_action.triggered.connect(lambda: self.obj.active_editor.setAlignment(Qt.AlignRight))
        format_toolbar.addAction(self.obj.alignr_action)
        format_menu.addAction(self.obj.alignr_action)

        self.obj.alignj_action = QAction(QIcon(os.path.join(path_to_images_icones, 'edit-alignment-justify.png')), "Justify", self.obj)
        self.obj.alignj_action.setStatusTip("Justify text")
        self.obj.alignj_action.setCheckable(True)
        self.obj.alignj_action.triggered.connect(lambda: self.obj.active_editor.setAlignment(Qt.AlignJustify))
        format_toolbar.addAction(self.obj.alignj_action)
        format_menu.addAction(self.obj.alignj_action)

        format_group = QActionGroup(self.obj)
        format_group.setExclusive(True)
        format_group.addAction(self.obj.alignl_action)
        format_group.addAction(self.obj.alignc_action)
        format_group.addAction(self.obj.alignr_action)
        format_group.addAction(self.obj.alignj_action)

        format_menu.addSeparator()

        # A list of all format-related widgets/actions, so we can disable/enable signals when updating.
        self.obj._format_actions = [
            self.obj.fonts,
            self.obj.fontsize,
            self.obj.bold_action,
            self.obj.italic_action,
            self.obj.underline_action,
            # We don't need to disable signals for alignment, as they are paragraph-wide.
        ]
        
        
        



class DictionaryTree(QtWidgets.QWidget):
    '''Which this class/object you can create a tree widget with a given dictionary, which you can edit in this way you want.'''
    def __init__(self, dictionary):
        super().__init__()
        self.setWindowTitle("Dictionary Tree")
        self.resize(400, 300)

        self.dictionary = dictionary

        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderLabels(["Key", "Value"])

        self.populate_tree_widget()

        self.addButton = QtWidgets.QPushButton("Add")
        self.addButton.clicked.connect(self.add_key_value)

        self.deleteButton = QtWidgets.QPushButton("Delete")
        self.deleteButton.clicked.connect(self.delete_selected_item)

        self.editButton = QtWidgets.QPushButton("Edit")
        self.editButton.clicked.connect(self.edit_selected_value)

        layout = QtWidgets.QVBoxLayout(self)#The Q..H/V.. stays for Horizontal/Vertical
        horizontal_layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.treeWidget)
        horizontal_layout.addWidget(self.addButton)
        horizontal_layout.addWidget(self.deleteButton)
        horizontal_layout.addWidget(self.editButton)
        layout.addLayout(horizontal_layout)

    def populate_tree_widget(self):
        self.treeWidget.clear()
        for key, values in self.dictionary.items():
            parent_item = QtWidgets.QTreeWidgetItem(self.treeWidget, [key, ""])
            for value in values:
                value_item = QtWidgets.QTreeWidgetItem(parent_item, ["", str(value)])
                parent_item.addChild(value_item)
            self.treeWidget.addTopLevelItem(parent_item)
            parent_item.setExpanded(True)

    def add_key_value(self):
        selected_item = self.treeWidget.currentItem()
        if selected_item:
            if selected_item.parent():
                # Add value to selected key
                key = selected_item.parent().text(0)
                value, ok = QtWidgets.QInputDialog.getText(self, "Add Value", "Enter value:")
                if ok and value:
                    self.dictionary[key].append(value)
                    value_item = QtWidgets.QTreeWidgetItem(selected_item.parent(), ["", value])
                    selected_item.parent().addChild(value_item)
            else:
                # Add new key-value pair
                key, ok = QtWidgets.QInputDialog.getText(self, "Add Key", "Enter new key:")
                if ok and key:
                    value, ok = QtWidgets.QInputDialog.getText(self, "Add Value", "Enter value:")
                    if ok and value:
                        self.dictionary[key] = [value]
                        parent_item = QtWidgets.QTreeWidgetItem(self.treeWidget, [key, ""])
                        value_item = QtWidgets.QTreeWidgetItem(parent_item, ["", value])
                        parent_item.addChild(value_item)
                        self.treeWidget.addTopLevelItem(parent_item)
                        parent_item.setExpanded(True)

    def delete_selected_item(self):
        selected_item = self.treeWidget.currentItem()
        if selected_item:
            if selected_item.parent():
                # Delete selected value
                parent_item = selected_item.parent()
                key = parent_item.text(0)
                index = parent_item.indexOfChild(selected_item)
                del self.dictionary[key][index]
                parent_item.removeChild(selected_item)
            else:
                # Delete selected key and all its values
                key = selected_item.text(0)
                del self.dictionary[key]
                self.treeWidget.invisibleRootItem().removeChild(selected_item)

    def edit_selected_value(self):
        selected_item = self.treeWidget.currentItem()
        if selected_item and selected_item.parent():
            parent_item = selected_item.parent()
            key = parent_item.text(0)
            index = parent_item.indexOfChild(selected_item)
            value, ok = QtWidgets.QInputDialog.getText(self, "Edit Value", "Enter new value:", QtWidgets.QLineEdit.Normal, selected_item.text(1))
            if ok:
                self.dictionary[key][index] = value
                selected_item.setText(1, value)
    def get_dict(self):
        return self.dictionary
    
    def update_dict(self, new_dict):
        self.dictionary = new_dict
        self.populate_tree_widget()

class DictionaryTree_Folder(QtWidgets.QWidget):
    """Object to navigate through a specified folder and its subfolders. You can add, edit and delete folders. 
    when edith_permision == False, Taht means you dont have permision to edit the folder structure. Set it in the __init__ method."""
    def __init__(self, obj, directory, edit_permision= True):
        super().__init__()
        self.setWindowTitle("Dictionary Tree")
        self.resize(400, 300)

        self.directory = directory
        self.selected_folder_path = None
        self.obj = obj

        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderLabel("Folder")

        self.populate_tree_widget_directory(self.directory)

        self.treeWidget.itemSelectionChanged.connect(self.folder_selected)
        self.treeWidget.itemDoubleClicked.connect(self.folder_doubleselected)
        
        layout = QtWidgets.QVBoxLayout(self)#The Q..H/V.. stays for Horizontal/Vertical
        layout.addWidget(self.treeWidget)

        if edit_permision:
            self.addButton = QtWidgets.QPushButton("Add")
            self.addButton.clicked.connect(self.add_folder)

            self.editButton = QtWidgets.QPushButton("Edit")
            self.editButton.clicked.connect(self.edit_folder)

            self.deleteButton = QtWidgets.QPushButton("Delete")
            self.deleteButton.clicked.connect(self.delete_folder)
            
            horizontal_layout = QtWidgets.QHBoxLayout()
            horizontal_layout.addWidget(self.addButton)
            horizontal_layout.addWidget(self.deleteButton)
            horizontal_layout.addWidget(self.editButton)
            layout.addLayout(horizontal_layout)

        

    def populate_tree_widget_directory(self, start_folder, start_name="Bibliothek"):
        """
        Füllt das Tree Widget mit den Ordnern und Unterordnern des Startordners.

        Args:
            start_folder (str): Der Startordner, von dem aus der Tree Widget aufgebaut wird.
        """
        self.treeWidget.clear()
        start_item = QtWidgets.QTreeWidgetItem(self.treeWidget, [start_name])
        start_item.folder_path = start_folder
        self.add_subfolders(start_item, start_folder)

    def add_subfolders(self, parent_item, folder_path):
        """
        Fügt dem übergeordneten Element die Unterordner als Tree Widget-Elemente hinzu.

        Args:
            parent_item (QTreeWidgetItem): Das übergeordnete Element, zu dem die Unterordner hinzugefügt werden sollen.
            folder_path (str): Der Pfad des übergeordneten Ordners.
        """
        for folder_name in [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) and f != "User_Data"]:
            folder_item = QtWidgets.QTreeWidgetItem(parent_item, [folder_name])
            folder_item.folder_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(folder_item.folder_path):
                self.add_subfolders(folder_item, folder_item.folder_path)
            if self.has_csv_file(folder_item.folder_path):
                folder_item.setForeground(0, QtGui.QBrush(QtGui.QColor("red")))  # Mark the folder item as red

    def has_csv_file(self, folder_path):
        """
        Überprüft, ob ein Ordner eine CSV-Datei enthält.

        Args:
            folder_path (str): Der Pfad des Ordners, der überprüft werden soll.

        Returns:
            bool: True, wenn der Ordner eine CSV-Datei enthält, ansonsten False.
        """
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                return True
        return False

    def folder_selected(self):
        """
        Wird aufgerufen, wenn ein Ordner im Tree Widget ausgewählt wird.
        """
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            self.selected_folder_path = selected_item.folder_path
        else:
            self.selected_folder_path = None

        #Change current selected folder in the obj. So in the parents class
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            self.selected_folder_path = selected_item.folder_path
        #self.obj.actualice_options(selected_item, self.selected_folder_path)
        self.obj.actualice_selection(selected_item, self.selected_folder_path)

    def add_folder(self):
        """
        Fügt einen neuen Ordner hinzu.
        """
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            folder_name, ok = QtWidgets.QInputDialog.getText(self, "Add Folder", "Enter folder name:")
            if ok and folder_name:
                new_folder_path = os.path.join(selected_item.folder_path, folder_name)
                os.makedirs(new_folder_path)
                new_folder_item = QtWidgets.QTreeWidgetItem(selected_item, [folder_name])
                new_folder_item.folder_path = new_folder_path

    def edit_folder(self):
        """
        Bearbeitet den Namen eines ausgewählten Ordners.
        """
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            folder_name, ok = QtWidgets.QInputDialog.getText(self, "Edit Folder", "Enter new folder name:", QtWidgets.QLineEdit.Normal, selected_item.text(0))
            if ok and folder_name:
                old_folder_path = selected_item.folder_path
                parent_item = selected_item.parent() if selected_item.parent() else selected_item
                new_folder_path = os.path.join(parent_item.folder_path, folder_name)
                os.rename(old_folder_path, new_folder_path)
                selected_item.setText(0, folder_name)
                selected_item.folder_path = new_folder_path

    def delete_folder(self):
        """
        Löscht den ausgewählten Ordner.
        """
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            folder_path = selected_item.folder_path
            reply = QtWidgets.QMessageBox.question(self, "Delete Folder", "Are you sure you want to delete this folder and its contents?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.remove_folder(folder_path)
                selected_item.parent().removeChild(selected_item)

    def remove_folder(self, folder_path):
        """
        Entfernt den Ordner und alle seine Inhalte.

        Args:
            folder_path (str): Der Pfad des zu entfernenden Ordners.
        """
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
        os.rmdir(folder_path)

    def folder_doubleselected(self):
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            self.selected_folder_path = selected_item.folder_path
        self.obj.actualice_options(selected_item, self.selected_folder_path)
        self.obj.actualice_selection(selected_item, self.selected_folder_path)
        
        #Start the main divers program to fill some flashcards
        self.obj.start_fill_bibli()
    
    def change_folder_path(self, new_path):
        self.populate_tree_widget_directory(new_path)
        self.selected_folder_path = new_path
        #self.obj.actualice_options(self.selected_folder_path)
        #self.obj.actualice_selection(self.selected_folder_path)
        



class SelectableTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected = False

    def setSelected(self, selected):
        self._selected = selected
        self.updateTextColors()

    def isSelected(self):
        return self._selected

    def updateTextColors(self):
        color = QtGui.QColor("blue") if self._selected else QtGui.QColor("black")
        for column in range(self.columnCount()):
            self.setForeground(column, QtGui.QBrush(color))


class DictionaryTree_select(QtWidgets.QWidget):
    def __init__(self, obj, dictionary):
        super().__init__()
        self.setWindowTitle("Dictionary Tree")
        self.resize(400, 300)
        self.obj = obj

        self.dictionary = dictionary

        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderLabels(["Key", "Value"])

        self.populate_tree_widget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.treeWidget)

        self.selected_keys = []
        self.selected_values = []

        self.treeWidget.itemClicked.connect(self.item_clicked)

    def populate_tree_widget(self):
        self.treeWidget.clear()
        for key, values in self.dictionary.items():
            parent_item = SelectableTreeWidgetItem(self.treeWidget)
            parent_item.setText(0, key)
            for value in values:
                value_item = SelectableTreeWidgetItem(parent_item)
                value_item.setText(1, value)
                parent_item.addChild(value_item)
            self.treeWidget.addTopLevelItem(parent_item)
            parent_item.setExpanded(True)

    def item_clicked(self, item, column):
        if isinstance(item, SelectableTreeWidgetItem):
            selected = not item.isSelected()
            item.setSelected(selected)
            key = item.text(0)
            value = item.text(1)

            if column == 0:
                # Key selected
                if selected:
                    self.select_values_of_key(key)
                else:
                    self.deselect_values_of_key(key)
            elif column == 1:
                # Value selected
                if selected:
                    self.select_key_of_value(key, value)
                else:
                    self.deselect_key_of_value(key, value)
        self.obj.format_vorlage = self.get_selected_dict()

    def select_values_of_key(self, key):
        try:
            if key not in self.selected_keys:
                self.selected_keys.append(key)
                values = self.dictionary[key]
                self.selected_values.extend(values)

                for top_level_item_index in range(self.treeWidget.topLevelItemCount()):
                    top_level_item = self.treeWidget.topLevelItem(top_level_item_index)
                    if top_level_item.text(0) == key:
                        for child_index in range(top_level_item.childCount()):
                            child_item = top_level_item.child(child_index)
                            child_item.setSelected(True)
        except:
            QMessageBox.about(self, "Error", "Please select a folder first")

    def deselect_values_of_key(self, key):
        try:
            if key in self.selected_keys:
                self.selected_keys.remove(key)
                values = self.dictionary[key]
                self.selected_values = [value for value in self.selected_values if value not in values]

                for top_level_item_index in range(self.treeWidget.topLevelItemCount()):
                    top_level_item = self.treeWidget.topLevelItem(top_level_item_index)
                    if top_level_item.text(0) == key:
                        for child_index in range(top_level_item.childCount()):
                            child_item = top_level_item.child(child_index)
                            child_item.setSelected(False)
        except:
            QMessageBox.about(self, "Error", "Please select a folder first")

    def select_key_of_value(self, key, value):
        if value not in self.selected_values:
            self.selected_values.append(value)
            if key not in self.selected_keys:
                self.selected_keys.append(key)
                for top_level_item_index in range(self.treeWidget.topLevelItemCount()):
                    top_level_item = self.treeWidget.topLevelItem(top_level_item_index)
                    if top_level_item.text(0) == key:
                        top_level_item.setSelected(True)

    def deselect_key_of_value(self, key, value):
        if value in self.selected_values:
            self.selected_values.remove(value)
            if key in self.selected_keys:
                self.selected_keys.remove(key)
                for top_level_item_index in range(self.treeWidget.topLevelItemCount()):
                    top_level_item = self.treeWidget.topLevelItem(top_level_item_index)
                    if top_level_item.text(0) == key:
                        top_level_item.setSelected(False)

    def get_selected_dict(self):
        selected_dict = {}
        for key, values in self.dictionary.items():
            if key in self.selected_keys:
                selected_dict[key] = []
                for value in values:
                    if value in self.selected_values:
                        selected_dict[key].append(value)
        return selected_dict

    def update_dict(self, new_dict):
        self.dictionary = new_dict
        self.populate_tree_widget()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    directory = r"_Data_Col"  # Setze den gewünschten Startordner
    dictionary_tree = DictionaryTree_Folder(directory)
    dictionary_tree.show()
    sys.exit(app.exec_())

