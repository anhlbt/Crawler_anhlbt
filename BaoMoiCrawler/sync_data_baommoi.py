
from alignment.forced_alignment import AlignmentAudio
from alignment.config import Config
import os, random
from os.path import isdir, join, exists
import shutil
import pandas as pd

def check_df(df):
    pass
    
        

if __name__=="__main__":
    
    config = Config()
    text_folder = config.elastic['text_folder']
    audio_folder = config.elastic['audio_folder']
    aligned_folder = config.elastic['aligned_foler']
    if not exists(aligned_folder):
        os.makedirs(aligned_folder)
        
    characters = config.aeneas['characters']
    temp_folder = config.sync['audio_temp_folder']
    if not exists(temp_folder):
        os.makedirs(temp_folder)    
    output_folder = config.sync['output_folder']
    if not exists(output_folder):
        os.makedirs(output_folder)      
    ignore_num_sentences= config.sync['num_sentences']
    
    df = pd.DataFrame(columns=['audio', 'content'])
        
    set_audio_files = set([d[:-2] for d in os.listdir(audio_folder) if not isdir(join(audio_folder, d))])
    lst_text_files = set([d[:-4] for d in os.listdir(text_folder) if not isdir(join(text_folder, d))])
    lst_audio_files = [d for d in os.listdir(audio_folder) if not isdir(join(audio_folder, d))]

    print(len(lst_text_files))
    count = 1
    for _file in set_audio_files:
        if _file in lst_text_files:
            print(_file)
            lst_rd = random.sample(['1','2', '8','9'], 4)  #random.choice(['1','2', '8','9'])  
            for engine_code in lst_rd:
                if "{0}_{1}".format(_file, engine_code) in lst_audio_files:           
                    audio_file = join(audio_folder, "{0}_{1}".format(_file, engine_code)) #lst_rd = random.sample(['1','2', '8','9'], 4)  #  
                    shutil.copyfile(audio_file, join(temp_folder, "{0}_{1}".format(_file, engine_code)))
                    script_file = join(text_folder, "{0}.txt".format(_file))
                    aligned_file =join(aligned_folder, "{0}.json".format(_file))
                      
                    align_obj = AlignmentAudio(audio_file, script_file, aligned_file, characters, output_folder)
                    align_obj.preprocessing_script()
                    align_obj.align_audio()
                    df_tmp = align_obj.read_fragments_to_df("{:06d}".format(count))
                    
                    if df_tmp.shape[0] > int(ignore_num_sentences):
                        df = df.append(df_tmp)                    
                        align_obj.plit_audio("{:06d}".format(count))
                        count += 1

                    break  
    df.to_csv(join(output_folder,"metadata.csv"), sep="|", index=False, header=False)
    print(count)