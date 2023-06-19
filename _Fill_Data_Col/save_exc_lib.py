#This is a library to save all kind of pandas array in an excell tabelle. There is a class for each kind of excell tabel. The class is called with the pandas array and the path to the excell file. The class has a method to save the pandas array in the excell file. The class has a method to read the pandas array from the excell file.

import pandas as pd
import numpy as np
import os



class OpenExcel:
    def __init__(self, path, format_question1 = ["Name"], format_question2=["je", "tu", "il", "nous", "vous", "ils"]):
        '''This is a library to save all kind of vocis, verbs, etc. in an excell tabelle.
        There is a class for each kind of excell tabel. The class is called with the pandas array and the path to the excell file.
        format_question1: Just put one string in the list. This is the name of the first column. For example: "Name"
        format_question2: Put all the names of the columns in the list. For example: ["je", "tu", "il", "nous", "vous", "ils"]'''
        
        self.format_question1 = format_question1
        self.format_question2 = format_question2
        self.format_columns = self.format_question1+self.format_question2
        self.path = path
        self.name_theme = path.split("\\")[-1].split(".")[0]#!!!! Maybe add this later
        #print(self.name_theme)
        #self.time_name = time_name!!!! Maybe add this later
        
        try:
            # Versuche, die Excel-Tabelle zu öffnen
            self.df = pd.read_csv(path)
            print("Excel-Tabelle geöffnet gelesen")
        except:
            # Falls die Excel-Tabelle nicht existiert, erstelle eine neue
            self.df = pd.DataFrame(columns=self.format_columns)
            print("Excel-Tabelle erstellt")
    
    def get_df(self):
        return self.df
    
    def get_collumns_list(self, collumn_name):
        '''This method returns the whole column as a list.
        Example:
        get_row_list("Name")
        ==> ["aller", "avoir", "être", "faire", "pouvoir", "vouloir"]'''
        return self.df[collumn_name].tolist()
    
    def get_row_elements_by_name(self, name, panda_array=False):
        """If you want to get the data of a specific column, you can use the method get_element_by_name_and_column
        Just put the name of the word which you want to get the data on the same row of this word.
        The whole row will be returned as a dictionary.
        If you want the panda array of the row, ==> panda_array=True
        """
        #Check if the name contains in the dataframe
        if name not in self.df[self.format_question1[0]].tolist():
            return None
        #Check if the panda array should be returned or the dictionary
        if panda_array:
            return self.df.loc[self.df[self.format_question1[0]] == name]
        else:
            result = self.df.loc[self.df[self.format_question1[0]] == name].to_dict(orient="records")[0]
            print(result)
            return result
        
    def save_df(self):
        # Speichern der Daten in der Excel-Tabelle
        self.df.to_csv(self.path, index=False)

    def add_data_to_df(self, name, data):
        '''This method adds data to the excel file. If the name is already in the excel file, the data will be updated.
        If the name is not in the excel file, a new row will be added.
        name: The name of the word which you want to add to the data.
        data: The data which you want to add to the excel file. It can be a dictionary or a list.
        Example:
        add_data_to_df("aller", {"je":"", "tu":"vas", "il":"", "nous":"", "vous":"allez", "ils":""})
        or
        add_data_to_df("aller", ["vais", "vas", "", "allons", "", "vont"])'''
        # Überprüfe, ob der Name schon in der Excel-Tabelle vorhanden ist
        if name in self.df[self.format_question1[0]].tolist():
            # Wenn der Name vorhanden ist, aktualisiere die Daten. Es wird geschaut, welche data besser ist. (die alte oder die Neue)
            #Zum Beispiel: wenn die alte "" ist, dann wird diese überschrieben mit der neuen data. Wenn die neue "", dann wird die alte behalten.
            #If the data array is a type == dictionary
            if type(data) == dict:
                for key, value in data.items():
                    if self.df.loc[self.df[self.format_question1[0]] == name, key].empty or self.df.loc[self.df[self.format_question1[0]] == name, key].values[0] == "":
                        self.df.loc[self.df[self.format_question1[0]] == name, key] = value
                        #print("if")
                    elif value != "":
                        self.df.loc[self.df[self.format_question1[0]] == name, key] = value
                        #print("elif")
                        
            #If the data array is a type == list
            if type(data) == list:
                for i in range(len(data)):
                    if self.df.loc[self.df[self.format_question1[0]] == name, self.format_question2[i]].empty or self.df.loc[self.df[self.format_question1[0]] == name, self.format_question2[i]].values[0] == "":
                        self.df.loc[self.df[self.format_question1[0]] == name, self.format_question2[i]] = data[i]
                    elif data[i] != "":
                        self.df.loc[self.df[self.format_question1[0]] == name, self.format_question2[i]] = data[i]
        else:
            # Wenn der Name nicht vorhanden ist, füge eine neue Zeile hinzu
            #If the data array is a type == dictionary
            if type(data) == dict:
                data_list = list(data.values())
                
                new_row = pd.DataFrame([[name]+data_list], columns=self.format_columns)
            elif type(data) == list:
                new_row = pd.DataFrame([[name]+ data], columns=self.format_columns)
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            
            
            
if __name__=="__main__":
    present_list = OpenExcel(r"_Data_Col\Franz\Verbs\conjugate\present.csv")
    present_list.add_data_to_df("aller", {"je":"", "tu":"vas", "il":"", "nous":"", "vous":"allez", "ils":""})
    present_list.add_data_to_df("aller", ["vais", "vas", "", "allons", "", "vont"])
    present_list.add_data_to_df("aller", ["", "vas", "va", "allons", "allez", "vont"])
    print(present_list.get_df())
    present_list.save_df()
    print(present_list.get_row_elements_by_name("aller", panda_array=False))