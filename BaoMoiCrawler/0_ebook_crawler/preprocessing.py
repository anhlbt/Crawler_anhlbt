import os
import time
from pydub import AudioSegment
from pydub.playback import play
from os.path import isdir, join, exists, basename
import shutil
import re

import zipfile


# This function does both comands, its search for zip files and extract it to a specific folder
# The user could use it to unpack his dataset into a specific folder


class Preprocessing():
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.lst_book = []
        
            
    def filter_file_by_ext(self, ext1='.txt'):
        lst = [d.split(".")[0] for d in os.listdir(input_folder) if d.endswith(ext1)]
        return lst
        
    def check_file_names(self,):
        '''
        return: check textbook have audiobook
        '''
        text_file_lst = self.filter_file_by_ext('.txt')
        for text in text_file_lst:
            book_name = text.split('-')[0]
            regex = re.compile(".*{0}*".format(book_name)) #get name of the book only
            self.lst_book.extend(list(filter(regex.match, self.filter_file_by_ext('.zip'))))
            self.lst_book.extend(list(filter(regex.match, self.filter_file_by_ext('.mp3'))))
            

    def merge_audio(self,chapters, output_name):
        audios = [AudioSegment.from_mp3(join(self.input_folder, output_name, mp3_chapter)) for mp3_chapter in chapters]
        print(audios)
        combined = audios[0]

        for wav in audios[1:]:
            combined = combined.append(wav)
        combined.export(join(self.input_folder,"{0}.mp3".format(output_name.split("_Audio")[0])), format="mp3")     
    
    
    def extract_and_merge(self,):
        zip_file_lst = self.filter_file_by_ext('.zip')
        for zip_file in zip_file_lst:

            book_name = zip_file.split('-')[0]
            book_name = book_name.replace("_", " ")
            regex = re.compile(".*{0}*".format(book_name))
            zipPath = join(self.input_folder, "{0}.zip".format(zip_file))
            with zipfile.ZipFile(zipPath, mode='r') as zipObj:
                chapter_lst = list(filter(regex.match,  zipObj.namelist())) #['A Case Of Identity - Chapter 01.mp3', 'A Case Of Identity - Chapter 02.mp3']
          
                if not exists(join(self.input_folder,zip_file)):
                    os.makedirs(join(self.input_folder,zip_file))
                    
                    for filename in zipObj.namelist():
                        if filename.endswith('.mp3') or filename.endswith('.wav'):
        #                     print('Extracting ' + filename + ' to: ' + self.input_folder)
                            zipObj.extract(filename, join(self.input_folder,zip_file))
                            if len(chapter_lst) == 1:
                                tmp = filename.replace(" - ", "-").replace(" ", "_").split(".mp3")[0].split("-")
                                shutil.copy(join(self.input_folder,zip_file,filename),join(self.input_folder,"{0}-{1}.mp3".format(tmp[1], tmp[0])))
        
                
                if len(chapter_lst) > 1:
                    print('merge audio files')
                    print(chapter_lst)
                    self.merge_audio(chapter_lst, zip_file)    
                     
                shutil.rmtree(join(self.input_folder,zip_file))

if __name__=="__main__":
    input_folder = '/home/anhlbt/Downloads/test'
    pre = Preprocessing(input_folder)
    pre.extract_and_merge()
    