from __future__ import unicode_literals
import pylast
import youtube_dl  # downloads youtube via links
import datetime  # date and time stamp
import re  # regular expression module used for searching patterns
from os import getcwd
from pydub import AudioSegment, silence
from urllib.parse import quote
from urllib.request import urlopen
from bs4 import BeautifulSoup

API_KEY = "a0472e3ba14a8c6b2d373f25f7214f47"
API_SECRET = "e3706cbf68860e14e3da9bf6968b66c4"
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
album = input('What is the album title?: ')


# MyLogger uses the Logger module to display error logs
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def times_to_stamps(x):
    times = [list(reversed(time.split(':'))) for time in x]
    new_times=[]
    for time in times:
        new_time = 0
        for index,unit in enumerate(time):
            new_time +=int(unit)*(60**index)
        new_times.append(new_time)
    newer_time=[0]
    for index,time in enumerate(new_times):
        newer_time.append(str(datetime.timedelta(seconds=time+sum(new_times[:index]))))
    return newer_time


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
    # release_date = album_information.get_release_date()
    # return release_date


def got_cover_art(artist):
    art = pylast.Album(artist, album, network)
    cover_art = art.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
    return cover_art


# Determines when video is done converting
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


# Dictates youtube video options based on arguments such as format and artist information
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
    pattern = r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern)  # compiles pattern
    x = p.findall(description)
    # print(x)
    return x


def convert_timestamps_to_milliseconds(timestamps):
    # take the list of track times
    # split each one by the colon, reverse each one
    # muliply by powers of 60 to get seconds
    # multiply by 1000 to get milliseconds
    splittimes = [list(reversed(s.split(':'))) for s in timestamps]
    newtimes = []
    for time in splittimes:
        newtime = 0
        for index, unit in enumerate(time):
            newtime += int(unit) * (60 ** index) * 1000
        newtimes.append(newtime)
    return newtimes


def split_tracks_using_milliseconds(audio, artist, timelist):
    cwd = getcwd()
    for i in range(len(timelist) - 1):
        track = audio[timelist[i]:timelist[i + 1]]
        track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, i), format='mp3', bitrate="320k")
    track = audio[timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, len(timelist) - 1), format='mp3', bitrate="320k")


def split_tracks_intelligently(audio, artist, timelist):
    cwd = getcwd()
    tolerance = 1500  # 3 seconds
    new_timelist = [timelist[0]]

    for i in range(1, len(timelist)):
        track = audio.get_sample_slice(timelist[i] - tolerance, timelist[i] + (tolerance // 2))
        x = silence.detect_silence(track, silence_thresh=track.dBFS, min_silence_len=10)[0]
        new_timestamp = timelist[i] - tolerance + (sum(x) / len(x)) + 2000
        new_timelist.append(new_timestamp)
        print(datetime.timedelta(seconds=new_timestamp / 1000))

    for i in range(len(new_timelist) - 1):
        track = audio[new_timelist[i]:new_timelist[i + 1]]
        track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, i), format='mp3', bitrate="320k")
    track = audio[new_timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}.mp3".format(cwd, artist, len(timelist) - 1), format='mp3', bitrate="320k")


def search_youtube():
    textToSearch = input("enter the name of the album you want") + ' full album'
    query = quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    link_list = ['https://www.youtube.com' + vid['href'] for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'})]
    link_list = [link for link in link_list if len(link) == 43]
    return link_list[0]


def main():
    # url ="https://www.youtube.com/watch?v=4o5baMYWdtQ"
    # url = "https://www.youtube.com/watch?v=-tT32VTll5M" #frank ocean - blonde no track times
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs" #tyler the creator - who dat boy
    url = "https://www.youtube.com/watch?v=D1ZpZ_dvd_4"  # artic monkey  with tracktimes in description
    # url = "https://www.youtube.com/watch?v=yzssslz4r70" #plantasia - mort garson with tracktimes in different format
    # url ="https://www.youtube.com/watch?v=q59ZZtiLgYU" # hot funky jazz tracklistings, longer than an hour
    # url = "https://www.youtube.com/watch?v=-tT32VTll5M"
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs"
    # url = "https://www.youtube.com/watch?v=B-QddLcds2U" #darkside of the moon - pinkfloyd
    # url ="https://www.youtube.com/watch?v=q59ZZtiLgYU" # hot funky jazz tracklistings, longer than an hour
    # url = search_youtube()

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
        # print(description)
        # print(title)
        # print(duration)
        # print(length)
        # print(album_info(artist))
        # print(artist)
        # print(description)
        # print(title)
        # print(duration)
        # print(artist)
        # print(length)

        if artist:
            print('The artist is {0}.'.format(artist))
            answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
            artist = answer if answer != '' else artist
        else:
            artist = input('There is no artist for this album. Who is the artist? ')
        ydl_opts['outtmpl'] = '/output/{0}/%(title)s.mp3'.format(artist)

    # find track times (if present)
    timestamps = find_timestamps(description)

    cwd = getcwd()
    audio_location = "{0}\output\{1}\{2}.mp3".format(cwd, artist, title)
    # print(audio_location)

    # download album
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])

    millitimes = convert_timestamps_to_milliseconds(timestamps)
    albumaudio = AudioSegment.from_file(audio_location)
    # split_tracks_using_milliseconds(albumaudio,artist,millitimes)
    split_tracks_intelligently(albumaudio, artist, millitimes)


main()
