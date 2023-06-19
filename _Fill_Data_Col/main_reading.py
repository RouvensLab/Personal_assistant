import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QTextDocument
from PyQt5.QtCore import Qt
import os

class TextDisplayWidget(QWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.text_edit.setText(self.text)
        self.text_edit.selectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_text(self, text):
        self.text = text
        self.text_edit.setPlainText(self.text)

    def set_font(self, font):
        self.text_edit.setFont(font)

    def set_format(self, format):
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(format)
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def on_selection_changed(self):
        selected_word = self.get_selected_word()
        if selected_word:
            print(f"Selected word: {selected_word}")

    def get_selected_word(self):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return None
        return cursor.selectedText()

class main_book:
    def __init__(self, path = None, text = None, html_text = None):
        self.text = text
        self.html_text = html_text
        self.path = path
        
        print(os.path.getsize(path))
        print(os.path.getmtime(path))
        print(os.path.getctime(path))
        #prepare the book
        
        self.open_book()
        self.transform_text()
        
    def get_book(self):
        return self.html_text
        
    def open_book(self):
        """This funktion open the book in the path and save the text in the variable text.
            For that it checks if it is a html or a plain text file. If it is a html file it will
            open it with the html parser, if it is a plain text file it will open it with the plain text parser."""
        with open(self.path, "r") as f:
            self.text = f.read()
    
    def transform_text(self):
        '''This funktion transform the the plain text to html format.'''
        self.html_text = self.plain_to_html(self.text)
    
    def plain_to_html(self, plain_text):
        html_text = "<html><body>{}</body></html>".format(plain_text.replace('\n', '<br>'))#replace the new line with a html new line
        return html_text
        
        
        

class MainWindow(QWidget):
    def __init__(self, path_book):
        super().__init__()
        self.text_display = None
        self.path_book = path_book
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Text Display')
        #Open the book in the path
        self.book = main_book(path = self.path_book)
        self.text_display = TextDisplayWidget(self.book.get_book())

        layout = QVBoxLayout()
        layout.addWidget(self.text_display)

        self.setLayout(layout)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    path = r"_Data_Col\Franz\Lectures\text_test.txt"
    window = MainWindow(path)
    window.show()
    sys.exit(app.exec_())