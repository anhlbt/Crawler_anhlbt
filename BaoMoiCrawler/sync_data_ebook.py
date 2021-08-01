
from alignment.forced_alignment import AlignmentAudio
from alignment.config import ConfigEbook
import os, random
from os.path import isdir, join, exists, dirname
import shutil
import pandas as pd
from utils.instalogger import InstaLogger

DIR = dirname(__file__)      

if __name__=="__main__":
    
    config = ConfigEbook(join(DIR, 'config.ini'))
    text_folder = config.sync_ebook_en['text_folder']
    audio_folder = config.sync_ebook_en['audio_folder']
    aligned_folder = config.sync_ebook_en['aligned_foler']
    if not exists(aligned_folder):
        os.makedirs(aligned_folder)
        
    characters = config.sync_ebook_en['characters']
    language = config.sync_ebook_en['task_language']
    # temp_folder = config.sync_ebook_en['audio_temp_folder']
    # if not exists(temp_folder):
    #     os.makedirs(temp_folder)    
    output_folder = config.sync_ebook_en['output_folder']
    if not exists(output_folder):
        os.makedirs(output_folder)      
    ignore_num_sentences= config.sync_ebook_en['num_sentences']
    
    df = pd.DataFrame(columns=['audio', 'content'])
    # check extension file    
    set_audio_files = set([d[:-4] for d in os.listdir(audio_folder) if d.endswith(".mp3")])
    lst_text_files = set([d[:-4] for d in os.listdir(text_folder) if d.endswith(".txt")])
    # lst_audio_files = [d for d in os.listdir(audio_folder) if not isdir(join(audio_folder, d))]

    # set_audio_files = [_file.replace("_"," ").replace("-", " by ") for _file in set_audio_files]
        

    print("total file: ",len(lst_text_files))
    count = 1
    for _file in set_audio_files:
        # _file = _file.replace("_"," ").replace("-", " by ")
        if _file.replace("_"," ").replace("-", " by ") in lst_text_files: #check name audio & text file
            try:
                InstaLogger.logger().info('file: %s' %(_file))
                audio_file = join(audio_folder, "{0}.mp3".format(_file)) #lst_rd = random.sample(['1','2', '8','9'], 4)  #  
                # shutil.copyfile(audio_file, join(temp_folder, "{0}.mp3".format(_file)))
                script_file = join(text_folder, "{0}.txt".format(_file))
                aligned_file =join(aligned_folder, "{0}.json".format(_file))
                    
                align_obj = AlignmentAudio(audio_file, script_file, aligned_file, characters, output_folder,language)
                align_obj.preprocessing_script()
                align_obj.align_audio()

                # #split audio #no need when sync ebook
                # df_tmp = align_obj.read_fragments_to_df("{:06d}".format(count))
                
                # if df_tmp.shape[0] > int(ignore_num_sentences):
                #     df = df.append(df_tmp)                    
                #     align_obj.plit_audio("{:06d}".format(count))
                #     count += 1
            except Exception as ex:
                InstaLogger.logger().error(ex)
        else:
            InstaLogger.logger().info('cannot precess: %s' %(_file))

    # df.to_csv(join(output_folder,"metadata.csv"), sep="|", index=False, header=False)
    