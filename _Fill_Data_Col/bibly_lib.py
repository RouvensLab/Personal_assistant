#This is a library to contorl were things are stored. So in which folder and directory

import os
import sys
import json
import shutil
import pandas as pd
from save_exc_lib import OpenExcel


class BibliAssistant:
    '''This is the main program where the whole data is stored. Only this class has access to the files in the folders.'''
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.options = self.get_main_options()
        self.aktive_subject = self.options["aktive_subject"]
        self.all_subjects = self.get_subject_folders()
        
        #here are all variables which store some data from the folders
        self.load_aktive_subject_folder()
        self.on_subject_change_callback = []
        
    def on_subject_change(self, callback_funktion):
        """This method adds a callback function to the list of callback functions.
        The argument is the self.aktive_subject_folder"""
        self.on_subject_change_callback.append(callback_funktion)
        
    def on_subject_change_delet(self, callback_funktion):
        self.on_subject_change_callback.remove(callback_funktion)
    
    def set_active_folder_of_active_subject(self, new_folder_path):
        self.options["aktive_folder_of_subjects"][self.aktive_subject] = new_folder_path
        self.save_main_options()
    
    def change_aktive_subject(self, new_subject):
        self.aktive_subject = new_subject
        self.options["aktive_subject"] = new_subject
        self.save_main_options()
        self.load_aktive_subject_folder()
        self.update_aktive_folder_of_other_objects()
        
    def load_aktive_subject_folder(self):
        if self.aktive_subject == "Allgemein":
            self.aktive_subject_folder = self.folder_path
        else:
            self.aktive_subject_folder = os.path.join(self.folder_path, self.aktive_subject)
            
    def update_aktive_folder_of_other_objects(self):
        for callback_funktion in self.on_subject_change_callback:
            callback_funktion(self.aktive_subject_folder)
        
        
    
    def search_names_in_folder(self, name):
        found_names = {}
        folder_path = self.aktive_subject_folder
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                #Check if there is a json file named _folder_data.json
                # if file_name == "_folder_data.json":
                #     file_path = os.path.join(root, file_name)
                #     format_vorlage = self.open_info_js(file_path)
                #     for key, value in format_vorlage.items():
                #         OpenExcel(os.path.join(root, key+".csv"), ["Name"], value)
                        
                        
                if file_name.endswith('.csv'):
                    file_path = os.path.join(root, file_name)
                    df = pd.read_csv(file_path)
                    matching_rows = df[df.iloc[:, 0] == name]
                    if not matching_rows.empty:
                        #Founded maches
                        found_n = matching_rows.to_dict(orient="records")
                        found_names[file_name] = found_n

        return found_names
    
    def open_info_js(self, folder_path):
        '''This method opens a json file and returns the data.
        Data contains the self.format_vorlage of all the csv files in this folder.
        Also there can be other data in the json file.
        
        The name of the json file is _folder_data.json'''
        path = os.path.join(folder_path, "_folder_data.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    
    def get_main_options(self):
        '''Returns the main options of the assistant over the whole folders'''
        path = os.path.join(self.folder_path, "info_data.json")
        with open(path, "r") as f:
            options = json.load(f)
        return options
    
    def save_main_options(self):
        '''Saves the main options of the assistant over the whole folders'''
        path = os.path.join(self.folder_path, "info_data.json")
        with open(path, "w") as f:
            json.dump(self.options, f)
    
    def get_subject_folders(self):
        folders = {"Allgemein": True}
        for item in os.listdir(self.folder_path):
            item_path = os.path.join(self.folder_path, item)
            if os.path.isdir(item_path):
                folders[item] = item_path
        return folders

    def get_theme_folders(self, subject):
        folders = {}
        directory = os.path.join(self.folder_path, subject)
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                folders[item] = item_path
        return folders
    
    def archive_main_folder(self, archive_name):
        if not os.path.exists(self.folder_path):
            print(f"Folder '{self.folder_path}' does not exist.")
            return f"Folder '{self.folder_path}' does not exist."

        if os.path.exists(archive_name):
            print(f"Archive '{archive_name}' already exists.")
            return f"Archive '{archive_name}' already exists."

        try:
            shutil.make_archive(archive_name, 'zip', self.folder_path)
            print(f"Folder '{self.folder_path}' successfully archived as '{archive_name}.zip'.")
            return f"Folder '{self.folder_path}' successfully archived as '{archive_name}.zip'."
        except Exception as e:
            print(f"Error archiving folder: {str(e)}")
            return f"Error archiving folder: {str(e)}"
    
if __name__ == "__main__":
    assistant = BibliAssistant(r"_Data_Col")
    print(assistant.get_subject_folders())
    print(assistant.get_theme_folders("Franz"))