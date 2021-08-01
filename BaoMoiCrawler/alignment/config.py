import configparser
import os
import logging
from os.path import join, dirname, exists

class Config():
    def __init__(self, config_fname='config.ini'):
        config = configparser.ConfigParser()
        config.sections()
        logging.info('Load configure from %s', config_fname)
        config.read(config_fname)
            
        self.aeneas = config['aeneas']
        self.elastic = config['elasticsearch']
        self.sync = config['sync']

class ConfigEbook():
    def __init__(self, config_fname='config.ini'):
        config = configparser.ConfigParser()
        # config.sections()
        logging.info('Load configure from %s', config_fname)
        config.read(config_fname)
            
        self.sync_ebook_en = config['sync_ebook_en']
