#insert ebook

from os.path import isdir, join, exists, basename
from utils.db import *
import re, os
from sqlalchemy.ext import mutable
mutable.MutableDict.associate_with(JsonEncodedDict)

def filter_file_by_ext(input_folder, ext1='.txt'):
    lst = [d.split(".")[0] for d in os.listdir(input_folder) if d.endswith(ext1)]
    return lst

def check_file_names(input_folder):

    lst_book = []
    text_file_lst = set(filter_file_by_ext(input_folder, ext1='.json'))
    audio_file_lst = set(filter_file_by_ext(input_folder, ext1='.mp3'))
    jpg_file_lst = set(filter_file_by_ext(input_folder, ext1='.jpg'))
    text_file_lst.intersection(audio_file_lst,jpg_file_lst)
        
    return text_file_lst    
        
        
if __name__=="__main__":
    input_folder= r'/home/anhlbt/Downloads/A2 Elementary'
    lst_file = check_file_names(input_folder)
    print("end...")
    for file in lst_file:
        json_book = load_json_from_file(join(input_folder, "{0}.json".format(file)))
        dbms = MyDatabase('SQLITE', dbname='app.db')
        post = Post(title=file, summary=file.replace("_", " "), body = "", json_book = json_book,
                    image="{0}.jpg".format(file), topic = "ebook")
        dbms.add_post(post)
        
    print("  ")
               