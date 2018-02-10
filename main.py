from __future__ import unicode_literals
import youtube_dl #downloads youtube via links
import datetime #date and time stamp
import re #regular expression module used for searching patterns

from musixmatch import Musixmatch


#MyLogger uses the Logger module to display error logs
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

#Determines when video is done converting
def search_title():
    musixmatch = Musixmatch('aadefa8e37881923e8db0e2456f30a48')
    pass

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


###################################################################################
#code that works with audio and can be repurposed
# from pydub import AudioSegment
# from os import listdir, stat, mkdir, getcwd
# from os.path import isfile, join
#
#
# def is_wav_file(cwd, fname):
#     if len(fname) < 4:
#         return False
#     else:
#         return isfile(join(cwd, fname)) and fname[-3:] == 'wav'
#
#
# def main():
#     op = 'output'
#     try:
#         stat(op)
#     except:
#         mkdir(op)
#
#     cwd = getcwd()
#     wavfiles = [f for f in listdir(cwd) if is_wav_file(cwd, f)]
#     for fname in wavfiles:
#         wav = AudioSegment.from_wav(fname)
#         wav.export('{0}/{1}/{2}mp3'.format(cwd, op, fname[:-3]), format="mp3", bitrate='320k')
#
#
###########################################################################################
# code that searches google images
import urllib3
import simplejson
import cStringIO


#def Parser():
   # Searcher = urllib3.build_opener()
    #Search_Word = title
    #Search_Index = 0
    #Search_URL = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + Search_Word + "&start=" + Search_Index
    #S= Searcher.open(Search_URL)
    #Output = simplejson.load(S)

############################################################################

