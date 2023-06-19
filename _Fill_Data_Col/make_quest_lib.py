#This is a library to make questions based on a some data, which are given by the other library class save_exc_lib.py. The class is called with the path to the excell file. The class has a method to make a question based on the data in the excell file. The class has a method to get the data from the excell file.
import sys
import os
import json
sys.path.append("_Fill_Data_Col")

from save_exc_lib import OpenExcel
import pandas as pd
import random
import math

class quest_answ:
    def __init__(self, data_managers, sel_format):
        """Give the data_manger object to the data_manager in the parameter.
        Beschreibe es so: dict = {}"""
        self.data_managers = data_managers
        #print(self.data_managers)
        
        self.sel_format = sel_format
        #search the directory of the data_manager and look if there even are User_Data files (.csv) in the directory in a folder named User_Data
        self.dir_User_Data = os.path.join(self.data_managers["path"], "User_Data")
        #Check if this directory exist, if not, then create it
        if not os.path.exists(self.dir_User_Data):
            os.mkdir(self.dir_User_Data)
        
        self.User_Data_abs_pos_dict = {}
        self.User_Data_abs_neg_dict = {}
        self.User_Data_abs_pos_dict = self.load_make_User_Data(self.dir_User_Data, "_pos")
        self.User_Data_abs_neg_dict = self.load_make_User_Data(self.dir_User_Data, "_neg")
        #print("Pos:", self.User_Data_abs_pos_dict)
        #print("Neg:", self.User_Data_abs_neg_dict)
        
        self.act_quest_answ = {}
        
    def set_sel_format(self, sel_format):
        self.sel_format = sel_format
    
    def load_make_User_Data(self, dir, pos_neg_name):
        '''This function loads the User_Data from the directory dir. If there is no User_Data.csv file in the directory, then it creates a new one.
        Or whene there arent data, it makes a new one. That counts for the whole data_format. So nothing gets lost.'''
        User_Data_abs_dict = {}
        for key, value in list(self.data_managers.items())[1:]:
            end_name = "User_Data_"+key+pos_neg_name+".csv"
            path_User_Data = os.path.join(dir, end_name)
               
            #if there exist a Excelfile named User_Data+...+.csv, then load the data from it
            if os.path.exists(path_User_Data):
                User_Data = pd.read_csv(path_User_Data)
                User_Data = self.actualize_User_Data_with_data_manager(User_Data, value)
                #User_Data.to_csv(path_User_Data, index = False)
            #Otherwise create a new one
            else:
                #print("There is no User_Data.csv file in the directory: ", dir)
                #Get columns of the data_manager pandas dataframe == value
                #print(value)
                columns = value.get_df().columns
                User_Data = pd.DataFrame(columns = columns)
                User_Data = self.actualize_User_Data_with_data_manager(User_Data, value)
                User_Data.to_csv(path_User_Data, index = False)
                #print(self.User_Data)
            User_Data_abs_dict[key] = User_Data
        return User_Data_abs_dict
    
    def actualize_User_Data_with_data_manager(self, User_data, data_manager):
        """This function checks if the User_Data has the same columns as the data_manager. If not, it adds the missing columns to the User_Data."""
        #get the names of the columns of the data_manager
        data_manager_columns = data_manager.get_collumns_list("Name")
        #print("Data_manager columns:",data_manager_columns)
        #get the names of the columns of the User_Data
        User_data_columns = User_data["Name"].tolist()
        #print("User_data_columns:",User_data_columns)
        #get the names of the columns of the User_Data, which are not in the data_manager
        columns_to_add = list(set(User_data_columns) ^ set(data_manager_columns))
        #Get columns of the data_manager pandas dataframe == value
        columns = data_manager.get_df().columns
        value_of_every_key = 1 #This is the value of every key in the User_Data that is new. So we begin with 1 and not with 0
        my_dict = {key: value_of_every_key for key in columns}
        #add the columns to the User_Data
        for column_name in columns_to_add:
            #print(column_name)
            my_dict["Name"] = column_name
            # Create a new DataFrame with a single row
            new_row = pd.DataFrame(my_dict, index=[0])

            #add the column to the User_Data pandas dataframe
            User_data = pd.concat([User_data, new_row], ignore_index=True)
        return User_data
    
    def get_options(self):
        return self.all_options
    
    def actualize_options(self, options):
        self.options = options
        
    def get_options(self):
        return self.options
    
    def calculate_percent(self, richtige_csv, falsche_csv, sel_format):
        #print(richtige_csv)
        #print(iter(sel_format.keys()))
        #Bereitet ein leeres DataFrame vor
        index_df = richtige_csv[list(sel_format.keys())[0]]["Name"]
        result_df = pd.DataFrame(index=index_df)  # Erstelle ein leeres DataFrame mit dem Index aus der ersten Tabelle

        for key_utheme, value_df in sel_format.items():  # Geht jedes Zeit/Unterthema durch
            richtig_df = richtige_csv[key_utheme]
            richtig_df = richtig_df.set_index('Name')

            falsch_df = falsche_csv[key_utheme]
            falsch_df = falsch_df.set_index('Name')

            richtig_werte = richtig_df[value_df]
            falsch_werte = falsch_df[value_df]

            prozentsatz = (falsch_werte.sum(axis=1) / (falsch_werte.sum(axis=1) + richtig_werte.sum(axis=1))) * 100

            result_df[key_utheme] = prozentsatz

        return result_df

    def sort_rows_by_average(self, df):
        # Berechne den Durchschnitt für jede Zeile
        df['Average'] = df.mean(axis=1)

        # Sortiere die Zeilen basierend auf den Durchschnittswerten
        sorted_df = df.sort_values('Average')

        # Entferne die Durchschnittsspalte
        #sorted_df = sorted_df.drop('Average', axis=1)

        return sorted_df
    
    def select_row_with_minimum_average(self, sorted_df):    
        min_average = sorted_df['Average'].min()
        min_rows = sorted_df[sorted_df['Average'] == min_average]
        print(min_rows)
        list_row_names = min_rows["Name"].tolist()
        if not min_rows.empty:  # Check if the index is empty
            selected_row = random.choice()
        else:
            selected_row = []  # Handle the case when no rows meet the criteria

        
        return selected_row
    
    def make_new_quest_old(self):
        #Look in the options which times are selected
        selected_times = self.sel_format
        #Go thrugh all the selected times and search the one word which has the lowest score.
        #If there are more than one word with the same score, then choose one of them randomly
        #Go thrugh the neg and pos User_Data and calculate the score in percent.
        sel_times_pos_dict = {}
        for key, value in self.User_Data_abs_pos_dict.items():
            if key in selected_times:
                sel_times_pos_dict[key] = value
        sel_times_neg_dict = {}
        for key, value in self.User_Data_abs_neg_dict.items():
            if key in selected_times:
                sel_times_neg_dict[key] = value
        #Now I have onely the selectet time in the sel_time_pos_dict and sel_time_neg_dict
        #print(sel_times_pos_dict)
        name_lowest = ""
        summe_lowest = 100000
        dict_of_lowest = {}
        #order the pandas array depending on the score
        for key, df_time_pos in sel_times_pos_dict.items():
            data_manager = self.data_managers[key]
            df_time_neg = sel_times_neg_dict[key]
            # Berechnen der Summe der Werte in "Spalte A" und "Spalte B" mit einer Liste von Spaltennamen
            columns = list(data_manager.get_df().columns)[1:]#Get the columns of the data_manager
            #print(columns)
            df_time_pos['Summe'] = df_time_pos[columns].sum(axis=1)-df_time_neg[columns].sum(axis=1)#Absolute berechnung von einer Row
            # Sortieren nach der Summe der Werte in "Spalte A" und "Spalte B"
            sorted_df = df_time_pos.sort_values(['Summe'], ignore_index=True)
            _name_lowest = sorted_df.iloc[0]["Name"]
            _summe_lowest = sorted_df.iloc[0]["Summe"]
            #print(_name_lowest, _summe_lowest)
            if _summe_lowest < summe_lowest:
                if self.arent_there_solutions(data_manager.get_row_elements_by_name(_name_lowest, False)):
                    name_lowest = _name_lowest
                    summe_lowest = _summe_lowest
                    key_lowest = key
                    dict_of_lowest = {}
                    dict_of_lowest[key] = [_name_lowest, data_manager.get_row_elements_by_name(name_lowest, False)]
            if _summe_lowest == summe_lowest:
                if self.arent_there_solutions(data_manager.get_row_elements_by_name(_name_lowest, False)):
                    dict_of_lowest[key] = [_name_lowest, data_manager.get_row_elements_by_name(_name_lowest, False)]
        
        #get a random key from the dict_of_lowest
        random_key_lowest = random.choice(list(dict_of_lowest.keys()))
        name = dict_of_lowest[random_key_lowest][0]
        #print(dict_of_lowest)
        #Give formatforlage to the quest
        return name, {random_key_lowest: list(dict_of_lowest[random_key_lowest][1])[1:]}
                
    
    def make_new_quest(self):
        #Go thrugh all the selected times and search the one word which has the lowest score.
        #If there are more than one word with the same score, then choose one of them randomly
        #Calculate the summary of the rows and calculate the percent of the correct answers
        csv_df_percent = self.calculate_percent(self.User_Data_abs_pos_dict, self.User_Data_abs_neg_dict, self.sel_format)
        #print(csv_df_percent)    
        sorted_df = self.sort_rows_by_average(csv_df_percent)
        #print(sorted_df)
        sel_name = self.select_row_with_minimum_average(sorted_df)
        #print(sel_name)
        #Find the name and the sel_format and pose the question
        dict_of_lowest = {}
        for key_utheme, value_list in self.sel_format.items():
            row_quest_ans = self.data_managers[key_utheme].get_row_elements_by_name(sel_name, True)
            if row_quest_ans is not None:
                row_quest_ans = row_quest_ans.loc[:, value_list].to_dict(orient="records")[0]#???!!!!! Hier muss noch die richtige valuelist ausgewählt werden
                dict_of_lowest[key_utheme] = row_quest_ans
                
        
        quest_ans_dict = {}
        result_dict = {}
        for key, value in dict_of_lowest.items():   
            #Check if there are solutions and not only nan, returns just the ones which have a solution
            working_sol = self.arent_there_solutions(value, True)
            quest_ans_dict[key] = working_sol
            result_dict[key] = list(working_sol.keys())
        return sel_name, result_dict


    def arent_there_solutions(self, forlage, return_all_with_solutions=False):
        if return_all_with_solutions:
            all_with_sol = {}
            if forlage == None:
                Exception("The forlage is None")
                return all_with_sol
            for key, value in forlage.items():
                #When the value is nan, then there is no solution
                if isinstance(value, str):
                    all_with_sol[key] = value
            return all_with_sol
                    
        else:
            for key, value in forlage.items():
                #When the value is nan, then there is no solution
                if not isinstance(value, str):
                    return False
            return True
        
    def check_answ(self, name, answ):#This can control answer whithout knowing which question was asked.
        '''This can control answer whithout knowing which question was asked. That is usefull, but also inefficient.'''
        #print(name+":::::", answ)
        correct_answ_dict = {}
        result = True
        for time_key, value in answ.items():
            if value != {}:
                data_manager = self.data_managers[time_key]
                correct_answ = data_manager.get_row_elements_by_name(name, False)
                correct_answ_dict[time_key] = correct_answ
                del correct_answ['Name']
                #print(correct_answ, value)
                for key, antwort in value.items():#Goes through 
                    loesung = correct_answ[key]
                    if antwort in [""]:
                        pass
                    else:
                        # Berechne den Unterschied zwischen der Antwort des Benutzers und der Lösung
                        unterschied = 0
                        for i in range(len(loesung)):
                            if i >= len(antwort):
                                # Die Eingabe des Benutzers ist kürzer als die Lösung
                                unterschied += 1
                            elif antwort[i] != loesung[i]:
                                # Die Buchstaben an dieser Stelle stimmen nicht überein
                                unterschied += 1
                        if unterschied == 0:
                            self.User_Data_abs_pos_dict[time_key].loc[self.User_Data_abs_pos_dict[time_key]['Name'] == name, key] += 1
                        else:
                            self.User_Data_abs_neg_dict[time_key].loc[self.User_Data_abs_neg_dict[time_key]['Name'] == name, key] += 1
                    result = False
        
        #Save the User_Data
        self.save_User_Data()
        return result, correct_answ_dict
    
    def get_score(self):
        pass
    
    def save_User_Data(self):
        for time_key, df in self.User_Data_abs_pos_dict.items():
            df.to_csv(os.path.join(self.dir_User_Data, "User_Data_"+time_key+"_pos.csv"), index=False)
        for time_key, df in self.User_Data_abs_neg_dict.items():
            df.to_csv(os.path.join(self.dir_User_Data, "User_Data_"+time_key+"_neg.csv"), index=False)
        
        
    def get_Users_Data(self):
        pass
    
if __name__ == "__main__":
    def open_info_js(folder_path):
        '''This method opens a json file and returns the data.
        Data contains the self.format_vorlage of all the csv files in this folder.
        Also there can be other data in the json file.
        
        The name of the json file is _folder_data.json'''
        path = os.path.join(folder_path, "_folder_data.json")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    
    verbs_con_directory = r"_Data_Col\Franz\Verbs\conjugate"
    #open the _folder_data.json file whith the data about the full format
    full_format_vorlage = open_info_js(verbs_con_directory)
    data_manager = {"path": verbs_con_directory}
    for key, value in full_format_vorlage.items():
        #print(key, value)
        verben_present = OpenExcel(os.path.join(verbs_con_directory, key+".csv"), ["Name"], value)
        data_manager[key] = verben_present
    sel_format = {"present": ["je", "tu", "il", "ils"]}
    teacher = quest_answ(data_manager, sel_format)
    
    #The funny part
    #print(teacher.make_new_quest())
    
    
    
    
    
    
    
    