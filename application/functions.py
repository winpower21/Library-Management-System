import os

def date_setter(date,):
    year, month, date = map(int,date.split("-"))
    return year, month, date

def create_folder(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        
