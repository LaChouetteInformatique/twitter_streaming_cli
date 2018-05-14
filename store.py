#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import json
from time import strftime
from os import path as os_path
from pathlib import Path as pathlib_Path

class not_so_super_store():
    """
    Callable Connector to store json to file
    """

    def __init__(
        self,
        output_folder='output/',
        output_files_prefix = 'Collect',
        #files_max_size = 2*1024*1024, # 2Mb
        #files_max_number = 5 # Number of different files before rollover
    ):
        # Name of the folder used to store every file : logs and gathered tweets
        # NOTE This folder will be created inside the current active directory
        self.__subPath__ = pathlib_Path(output_folder)
        # If subpath doesn't exist, mkdir
        # This folder will be used to store every files generated (log, txt, json)
        self.__subPath__.mkdir(parents=True, exist_ok=True)
        # Prefix used for files name generation
        self.__outputFilesPrefix__ = output_files_prefix
        self.__outputFilesBase__ = self.generate_file_name()

    def __call__(self, msg):
        """ Callable method to actually store stuff, exemple :
        store = not_so_super_store()
        store('test') # is equivalent as store.__call__('test')
        """
        # Generate JSON file and append it with tweet's JSON content
        with open(self.__outputFilesBase__+'.json', 'a', encoding='utf8') as file:
            #TODO try:
            #except:
            file.write(json.dumps(msg, ensure_ascii=False) )
            file.write('\n')
    
    
    def generate_file_name(self):
        ''' Output_Files Name Generation '''
        # Protection against long file names
        if (len(self.__outputFilesPrefix__) > 32):
            self.__outputFilesPrefix__ = self.__outputFilesPrefix__[:33]
        # Generate file name from path, prefix, and current time
        return os_path.join(self.__subPath__ , self.__outputFilesPrefix__ + '_' + strftime("%Y_%m_%d-%H_%M_%S"))

        # def convert_bytes(num):
    #     """
    #     this function will convert bytes to MB.... GB... etc
    #     """
    #     for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    #         if num < 1024.0:
    #             return "%3.1f %s" % (num, x)
    #         num /= 1024.0

    # def file_size(file_path):
    #     """
    #     this function will return the file size
    #     """
    #     if os.path.isfile(file_path):
    #         file_info = os.stat(file_path)
    #         return convert_bytes(file_info.st_size)

    # file = pathlib_Path() / 'doc.txt'  # or pathlib_Path('./doc.txt')
    # size = file.stat().st_size