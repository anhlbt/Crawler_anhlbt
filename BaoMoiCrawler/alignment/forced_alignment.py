# -*- coding: utf-8 -*-
from nltk import sent_tokenize
import re
import json
from pydub import AudioSegment
import os
from aeneas.exacttiming import TimeValue
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc
from os.path import join, exists
import pandas as pd
import aeneas
class AlignmentAudio(object):

    def __init__(self, audio_file, script_file, aligned_file, characters,output_folder,language='eng', \
        task_input_format='plain', task_output_format='json',audio_file_process_length = 0, task_custom_id='0001'):
        self.audio_file = audio_file
        self.script_file = script_file
        self.aligned_file = aligned_file
        self.output_folder = join(output_folder,"wavs")
        if not exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.characters = characters
        self.aligned = None

        configuration = TaskConfiguration()
        configuration[gc.PPN_TASK_LANGUAGE] = language
        configuration[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = task_input_format
        configuration[gc.PPN_TASK_OS_FILE_FORMAT] = task_output_format
        configuration[gc.PPN_TASK_IS_AUDIO_FILE_PROCESS_LENGTH] = audio_file_process_length
        configuration[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = 'offset'
        configuration[gc.PPN_TASK_ADJUST_BOUNDARY_OFFSET_VALUE] = -0.15
        
        configuration[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_MIN] = 0.2
        configuration[gc.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING] = 'REMOVE'
        configuration[gc.PPN_TASK_CUSTOM_ID] = task_custom_id
        
        
        self.configuration = configuration

    def preprocessing_script(self):
        '''
        # read script from script.txt, remove newlines, and splitting into sentences
        '''
        with open(self.script_file,"r") as script:
            new_text = script.read()
        # new_text = new_text.replace("\t","")    
        # new_text= new_text.split("- THE END -")[0]
        # new_text = re.sub(pattern=r'\n{2,10}',repl="\n(sil)\n",string=new_text)
        new_text = re.sub(self.characters, '', new_text)
        
        # new_text = new_text.lower()
        
        sentences = sent_tokenize(new_text)
        print("Number of sentences:", len(sentences))

        with open(self.script_file ,"w") as script:
            script.writelines("\n".join(sentences))
            

    def align_audio(self):
        '''
        split the audio using the script with aeneas
        '''
        aeneas.globalconstants.PPV_TASK_ADJUST_BOUNDARY_NONSPEECH_REMOVE= 'REMOVE'
        aeneas.globalconstants.PPN_TASK_ADJUST_BOUNDARY_NONSPEECH_STRING= 'task_adjust_boundary_nonspeech_string'
        config_string = "task_language=vie|os_task_file_format=json|is_text_type=plain| \
            task_adjust_boundary_algorithm=rateaggressive|task_adjust_boundary_rate_value=17| \
                task_adjust_boundary_nonspeech_min=0.1|task_adjust_boundary_nonspeech_string=sil"
                        
        # config_string = "task_language=vie|os_task_file_format=json|is_text_type=plain|\
        #     task_adjust_boundary_algorithm=offset|task_adjust_boundary_offset_value=-0.15|\
        #         task_adjust_boundary_nonspeech_min=0.2|\
        #             task_adjust_boundary_nonspeech_string=sil|task_custom_id=001|\
        #                 is_audio_file_process_length=0|is_text_file_ignore_regex=[*]"  
                        
        # config_string = "task_language=vie|os_task_file_format=json|is_text_type=plain|\
        #     task_adjust_boundary_algorithm=offset|task_adjust_boundary_offset_value=-0.25|\
        #         task_adjust_boundary_nonspeech_min=0.2"  
                                                                 
        task = Task(config_string=config_string)
        
        
        # task = Task()
        # task.configuration = self.configuration
        
        task.audio_file_path_absolute = self.audio_file
        task.text_file_path_absolute = self.script_file
        task.sync_map_file_path_absolute = self.aligned_file
        ExecuteTask(task).execute() # execute
        task.output_sync_map_file() # write the sync map to output file  
        
        # convert unicode to string
        # Since aeneas use python 2, and python 2 doesn't have string type, we need to convert it to python 3 string
        with open(self.aligned_file,"r") as output:
            self.aligned = json.load(output)
        for item in self.aligned['fragments']:
            item['lines'][0]=item['lines'][0].replace("sil", "\n\n")
        json.dump(fp=open(self.aligned_file,"w"),obj=self.aligned,ensure_ascii=False) 
        # return self.aligned         
        
    def plit_audio(self, prefix = "A"):
        # book = AudioSegment.from_wav(AUDIO_CHAPTER_FILE)
        book = AudioSegment.from_file(self.audio_file)

        # Splitting the audio book into sentences
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for i in range (0,len(self.aligned["fragments"])):
            fragment = self.aligned["fragments"][i]
            begin = float(fragment["begin"])*1000
            end = float(fragment["end"])*1000
            clip = book[begin:end]
            clip.export(join(self.output_folder, "{}_{}.wav".format(prefix, fragment["id"][-3:])),format="wav")

    def read_fragments_to_df(self,prefix = "A"):
        df = pd.DataFrame(columns=['audio', 'content'])
        for i, d in enumerate(self.aligned['fragments']):
            df.loc[i] = "{}_{}.wav".format(prefix, d["id"][-3:]), d['lines'][0]
        return df
        # df.to_csv(join(self.output_folder,"metadatas.csv"), sep="|", index=False, header=False)
        
