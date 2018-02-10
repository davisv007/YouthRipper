from __future__ import unicode_literals
import youtube_dl #downloads youtube via links
import datetime #date and time stamp
import re #regular expression module used for searching patterns
from googlesearch import search #search module


#MyLogger uses the Logger module to display error logs
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

#Determines when video is done converting
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

#Dictactes youtube video options based on arguments such as format and artist information
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/output/%(artist)s/%(title)s.mp3',
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
    url = "https://www.youtube.com/watch?v=FUXX55WqYZs" #tyler the creator - who dat boy
    # url = "https://www.youtube.com/watch?v=D1ZpZ_dvd_4" #artic monkey  with tracktimes in description
    # url = "https://www.youtube.com/watch?v=yzssslz4r70" #plantasia - mort garson with tracktimes in different format
    # url ="https://www.youtube.com/watch?v=q59ZZtiLgYU" # hot funky jazz tracklistings, longer than an hour

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # print(info_dict.keys())
        artist = info_dict['creator']
        description = info_dict['description']
        title = info_dict['title']
        duration = info_dict['duration']
        length =datetime.timedelta(seconds= duration)
        print(artist)
        # print(description)
        print(title)
        print(duration)
        length =datetime.timedelta(seconds= info_dict['duration'])
        print(artist)
        print(description)
        # print(title)
        print(length)



        if artist:
            print('The artist is {0}.'.format(artist))
            answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
            artist = answer if answer != '' else artist
        else:
            artist = input('There is no artist for this album. Who is the artist? ')
        ydl_opts['outtmpl']='/output/{0}/%(title)s.mp3'.format(artist)
    pattern =r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}' #Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second

    p = re.compile(pattern=pattern) #compiles pattern
    x=p.findall(description)
    print(x)
    print(len(x))
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])




main()
