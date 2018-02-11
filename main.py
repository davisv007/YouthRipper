from __future__ import unicode_literals
import youtube_dl #downloads youtube via links
import datetime #date and time stamp
import re #regular expression module used for searching patterns
from os import getcwd
from pydub import AudioSegment,silence


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
    'format': 'bestaudio',
    'outtmpl': '/output/%(artist)s/%(title)s.mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320'
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

def find_timestamps(description):
    pattern =r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}' #Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern) #compiles pattern
    x=p.findall(description)
    # print(x)
    return x

def convert_timestamps_to_milliseconds(timestamps):
    #take the list of track times
    #split each one by the colon, reverse each one
    #muliply by powers of 60 to get seconds
    #multiply by 1000 to get milliseconds
    splittimes=[list(reversed(s.split(':'))) for s in timestamps]
    newtimes=[]
    for time in splittimes:
        newtime=0
        for index,unit in enumerate(time):
            newtime+=int(unit)*(60**index)*1000
        newtimes.append(newtime)
    return newtimes

def split_tracks_using_milliseconds(audio,artist, timelist):
    cwd = getcwd()
    for i in range(len(timelist)-1):
        track = audio[timelist[i]:timelist[i+1]]
        track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist,i),format='mp3',bitrate="320k")
    track = audio[timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, len(timelist)-1), format='mp3',bitrate="320k")

def split_tracks_intelligently(audio,artist,timelist):
    cwd = getcwd()
    tolerance = 1500 #3 seconds
    new_timelist=[timelist[0]]
    for i in range(1,len(timelist)):
        track = audio.get_sample_slice(timelist[i]-tolerance,timelist[i]+tolerance)
        # print(len(track))
        # print(track.dBFS)
        x = silence.detect_silence(track,silence_thresh=track.dBFS,min_silence_len=10)[0]
        # print(x)
        new_timestamp = timelist[i]-tolerance+(sum(x)/len(x))+1000
        new_timelist.append(new_timestamp)
        print(datetime.timedelta(seconds=new_timestamp/1000))
        # break
        # track = audio[timelist[i]:timelist[i+1]]
        # track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist,i),format='mp3',bitrate="320k")
    for i in range(len(new_timelist)-1):
        track = audio[new_timelist[i]:new_timelist[i+1]]
        track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist,i),format='mp3',bitrate="320k")
    track = audio[new_timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, len(timelist)-1), format='mp3',bitrate="320k")

def main():

    # url ="https://www.youtube.com/watch?v=4o5baMYWdtQ"
    # url = "https://www.youtube.com/watch?v=-tT32VTll5M" #frank ocean - blonde no track times
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs" #tyler the creator - who dat boy
    # url = "https://www.youtube.com/watch?v=D1ZpZ_dvd_4" #artic monkey  with tracktimes in description
    # url = "https://www.youtube.com/watch?v=yzssslz4r70" #plantasia - mort garson with tracktimes in different format
    url = "https://www.youtube.com/watch?v=B-QddLcds2U" #darksid of the moon - pinkfloyd
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
        print(artist)
        print(length)



        if artist:
            print('The artist is {0}.'.format(artist))
            answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
            artist = answer if answer != '' else artist
        else:
            artist = input('There is no artist for this album. Who is the artist? ')
        ydl_opts['outtmpl']='/output/{0}/%(title)s.mp3'.format(artist)

    #find track times (if present)
    timestamps=find_timestamps(description)

    cwd = getcwd()
    audio_location = "{0}\output\{1}\{2}.mp3".format(cwd, artist,title)
    # print(audio_location)

    # download album
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])


    millitimes = convert_timestamps_to_milliseconds(timestamps)
    albumaudio = AudioSegment.from_file(audio_location)
    # # x =silence.detect_silence(albumaudio)
    # # print(x)
    # split_tracks_using_milliseconds(albumaudio,artist,millitimes)
    split_tracks_intelligently(albumaudio,artist,millitimes)



main()
