from __future__ import unicode_literals
import youtube_dl #downloads youtube via links
import datetime #date and time stamp
import re #regular expression module used for searching patterns
from musixmatch import Musixmatch
import pylast


API_KEY = "a0472e3ba14a8c6b2d373f25f7214f47"
API_SECRET = "e3706cbf68860e14e3da9bf6968b66c4"
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
album = input('What is the album title?: ')

#MyLogger uses the Logger module to display error logs
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

#Determines when video is done converting



def search_tracks(artist):
    album_tracks = pylast.Album(artist, album, network)
    tracks = album_tracks.get_tracks()
    # print(str(tracks[0]).split('-')[1])
    tracks = [str(track).split('- ')[1] for track in tracks]
    # [print(track) for track in tracks]
    return tracks


def album_info(artist):
    album_information = pylast.Album(artist, album, network)
    summary = album_information.get_wiki_summary()
    release_date = album_information.get_release_date()
    return release_date


def got_cover_art(artist):
    art = pylast.Album(artist, album, network)
    cover_art =  art.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
    return cover_art


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


#Dictactes youtube video options based on arguments such as format and artist information
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/output/%(artist)s/%(title)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320'
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


def main():

    # url ="https://www.youtube.com/watch?v=4o5baMYWdtQ"
    # url = "https://www.youtube.com/watch?v=-tT32VTll5M" #frank ocean - blonde no track times
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs" #tyler the creator - who dat boy
    url = "https://www.youtube.com/watch?v=D1ZpZ_dvd_4" #artic monkey  with tracktimes in description
    # url = "https://www.youtube.com/watch?v=yzssslz4r70" #plantasia - mort garson with tracktimes in different format
    # url ="https://www.youtube.com/watch?v=q59ZZtiLgYU" # hot funky jazz tracklistings, longer than an hour

    # url = "https://www.youtube.com/watch?v=-tT32VTll5M"
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # print(info_dict.keys())
        artist = info_dict['creator']
        description = info_dict['description']
        title = info_dict['title']
        duration = info_dict['duration']
        length = datetime.timedelta(seconds=duration)
        tracks = search_tracks(artist)
        summary = album_info(artist)
        genres = info_dict['categories']
        cover_art = got_cover_art(artist)
        album_information = {"summary": summary, "genre": genres, "album_length": length}
        # for key in album_information:
        #     print(album_information[key])
        # print(get_album_title(title, artist))
        # print(cover_art)
        # print(info_dict['categories'])
        # print(info_dict)
        # print(artist)
        # print(tracks)
        # # print(description)
        # print(title)
        # print(duration)
        # print(length)
        print(album_info(artist))



        # if artist:
        #     print('The artist is {0}.'.format(artist))
        #     answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
        #     artist = answer if answer != '' else artist
        # else:
        #     artist = input('There is no artist for this album. Who is the artist? ')
        # ydl_opts['outtmpl']='/output/{0}/%(title)s'.format(artist)
    pattern =r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}' #Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second

    p = re.compile(pattern=pattern) #compiles pattern
    x=p.findall(description)
    #print(x)
    # print(len(x))
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])




main()

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
# import urllib3
# import simplejson
# import cStringIO


#def Parser():
   # Searcher = urllib3.build_opener()
    #Search_Word = title
    #Search_Index = 0
    #Search_URL = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + Search_Word + "&start=" + Search_Index
    #S= Searcher.open(Search_URL)
    #Output = simplejson.load(S)

############################################################################

