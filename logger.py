#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import json
from time import strftime
from os import path as os_path
from pathlib import Path as pathlib_Path

class super_logger():
    """
    wrapper for logging class
    """

    def __init__(
        self, 
        output_file='output/',
        output_files_prefix = 'Collect',
        log_lvl = 1,
        txt_output = False
    ):
        # Name of the folder used to store every file : logs and gathered tweets
        # NOTE This folder will be created inside the current active directory
        self.sub_path = pathlib_Path(output_file)
        # If subpath doesn't exist, mkdir
        # This folder will be used to store every files generated (log, txt, json)
        self.sub_path.mkdir(parents=True, exist_ok=True)
        # Prefix used for files name generation
        self.output_files_prefix = output_files_prefix

        #https://docs.python.org/3.6/library/logging.html#logging-levels
        self.__log_lvl__ = [ 0, 10, 20, 30, 40, 50 ][log_lvl]
        # Log_lvl 0 from command-line mean "NONE", and not "NOTSET"
        # In case of "NONE", we raise a flag that will allow to skip all log events
        self.__noLogs__ = (self.__log_lvl__ == 0)

        if (not self.__noLogs__):

            self.__logger__ = logging.getLogger(__name__)
            self.__logger__.setLevel(self.__log_lvl__)

            self.__formatter__ = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # self.__FileHandler__ = logging.FileHandler(self.generate_file_name()+'.log')
            # https://docs.python.org/3.6/library/logging.handlers.html#rotatingfilehandler
            self.__FileHandler__ = RotatingFileHandler(
                self.generate_file_name()+'.log',
                mode='a',
                maxBytes=2*1024*1024, # 2Mb max size for log files
                backupCount=5,
                encoding="utf-8",
                delay=0
            )

            self.__FileHandler__.setLevel(self.__log_lvl__)
            self.__FileHandler__.setFormatter(self.__formatter__)

            self.__ConsoleHandler__ = logging.StreamHandler()
            self.__ConsoleHandler__.setLevel(self.__log_lvl__)
            self.__ConsoleHandler__.setFormatter(self.__formatter__)

            self.__logger__.addHandler(self.__FileHandler__)
            self.__logger__.addHandler(self.__ConsoleHandler__)

    def generate_file_name(self):
        ''' Output_Files Name Generation '''
        # Protection against long file names
        if (len(self.output_files_prefix) > 32):
            self.output_files_prefix = self.output_files_prefix[:33]
        # Generate file name from prefix, target(twitter account) and current time
        return os_path.join(self.sub_path , self.output_files_prefix + '_' + strftime("%Y_%m_%d-%H_%M_%S"))

    def __call__(self, lvl, msg):
        """ This method is the one who does write logs by calling self.__logger__
        You can directly call this method from outside with the object name you created, exemple :
        logger = super_logger(txt_output = True)
        logger('info','test') # is equivalent as logger.__call__('info','test')
        """
        if (not self.__noLogs__):
            # lvl can be int or string for more convenience
            # {0: 'NONE', 1: 'DEBUG', 2: 'INFO', 3: 'WARN', 4: 'ERROR', 5: 'CRITICAL'}
            if isinstance(lvl, int):
                if(lvl < 1 and lvl > 5):
                    return False
                lvl = ['NONE','debug','info','warn','error','critical'][lvl]
            else: # string
                lvl.lower()
                if lvl not in ['debug','info','warn','error','critical']:
                    return False
            # call logging.lvl(msg) with lvl being replaced by it's string value
            getattr(self.__logger__, lvl)(msg)
            return True

if __name__ == '__main__':
    print('hello i\'m logger.py!')