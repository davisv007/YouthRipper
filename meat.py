from __future__ import unicode_literals
import pylast
import youtube_dl  # downloads youtube via links
import datetime  # date and time stamp
import re  # regular expression module used for searching patterns
from os import getcwd
from pydub import AudioSegment, silence
import wikipedia
from urllib.parse import quote
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib import request
from mutagen.mp3 import EasyMP3 as MP3
from mutagen.id3 import ID3, APIC, error
import pathlib
import shutil

API_KEY = "a0472e3ba14a8c6b2d373f25f7214f47"
API_SECRET = "e3706cbf68860e14e3da9bf6968b66c4"
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


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
    new_times = []
    for time in times:
        new_time = 0
        for index, unit in enumerate(time):
            new_time += int(unit) * (60 ** index)
        new_times.append(new_time)
    newer_time = ['0:00:00']
    for index, time in enumerate(new_times):
        newer_time.append(str(datetime.timedelta(seconds=time + sum(new_times[:index]))))
    return newer_time


def search_tracks(artist, album):
    album_tracks = pylast.Album(artist, album, network)
    tracks = album_tracks.get_tracks()
    # print(str(tracks[0]).split('-')[1])
    tracks = [str(track).split('- ')[1] for track in tracks]
    # [print(track) for track in tracks]
    return tracks


def album_info(artist, album):
    album_information = pylast.Album(artist, album, network)
    summary = album_information.get_wiki_summary()
    # release_date = album_information.get_release_date()
    # return release_date


def got_cover_art(artist, album):
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
    pattern = r'[0-2]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern)  # compiles pattern
    x = p.findall(description)
    # print(x)
    return x


def convert_timestamps_to_milliseconds(timestamps):
    # take the list of track times
    # split each one by the colon, reverse each one
    # muliply by powers of 60 to get seconds
    # multiply by 1000 to get milliseconds
    [print(s) for s in timestamps]
    splittimes = [list(reversed(s.split(':'))) for s in timestamps]
    newtimes = []
    for time in splittimes:
        newtime = 0
        for index, unit in enumerate(time):
            newtime += int(unit) * (60 ** index) * 1000
        newtimes.append(newtime)
    return newtimes


def split_tracks_using_milliseconds(audio, artist, album,timelist, tracks):
    cwd = getcwd()
    for i in range(len(timelist) - 1):
        track = audio[timelist[i]:timelist[i + 1]]
        track.export(out_f="{0}\output\{1}\{2}\{3}.mp3".format(cwd, artist,album, artist + ' - ' + tracks[i]), format='mp3',
                     bitrate="320k")
    track = audio[timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}\{3}.mp3".format(cwd, artist,album, artist + ' - ' + tracks[-1]),
                 format='mp3', bitrate="320k")


def split_tracks_intelligently(audio, artist, album,timelist, tracks):
    cwd = getcwd()
    tolerance = 1500  # 3 seconds
    new_timelist = [timelist[0]]

    for i in range(1, len(timelist)):
        track = audio.get_sample_slice(timelist[i] - tolerance, timelist[i] + tolerance)
        x = silence.detect_silence(track, silence_thresh=track.dBFS, min_silence_len=10)[0]
        new_timestamp = timelist[i] - tolerance + (sum(x) / len(x)) + 2000
        new_timelist.append(new_timestamp)
        print(datetime.timedelta(seconds=new_timestamp / 1000))

    for i in range(len(new_timelist) - 1):
        track = audio[new_timelist[i]:new_timelist[i + 1]]
        track.export(out_f="{0}\output\{1}\{2}\{3}.mp3".format(cwd, artist, album,artist + ' - ' + tracks[i]), format='mp3',
                     bitrate="320k")
    track = audio[new_timelist[-1]:]
    track.export(out_f="{0}\output\{1}\{2}\{3}.mp3".format(cwd, artist,album, artist + ' - ' + tracks[-1]),
                 format='mp3', bitrate="320k")


def search_youtube(album):
    textToSearch = album + ' full album'
    query = quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    link_list = ['https://www.youtube.com' + vid['href'] for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'})]
    link_list = [link for link in link_list if len(link) == 43]
    return link_list[0]


# Gathers the time stamps of any albumn and displays in list of strings
def getsTimeStamps(albumnName, albumnArtist, maxlen):
    """

    :param albumnName: type user input
    :param albumnArtist: type user input
    :return: N/A
    """

    albumnInfo = wikipedia.page(albumnName + ' ' + albumnArtist)  # searches all wikipedia pages
    if albumnInfo == False:
        albumnInfo = wikipedia.page(albumnArtist + ' ' + albumnName)
        albumnInfoHtml = albumnInfo.html()
    else:
        albumnInfoHtml = albumnInfo.html()  # displays every listing on html plage

    pattern = r'[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second

    p = re.compile(pattern=pattern)  # compiles pattern
    timeStamps = p.findall(albumnInfoHtml)
    # print(timeStamps)
    return timeStamps[:maxlen]


def save_art(artwork_link, location, album):
    with open('{0}{1}\\{2}'.format(location, album,album+'.png'), 'wb') as f:
        f.write(request.urlopen(artwork_link).read())
        f.close()


def update_tags(location, artist, album, tracklist):
    # edit the ID3 tag to add the title, artist, artwork, date, and genre
    for index, title in enumerate(tracklist):
        # print(location+"{}.mp3".format(title))
        # break

        audiofile = MP3(location + "{0}\{1} - {2}.mp3".format(album, artist, title))
        try:
            audiofile.add_tags()
        except error:
            pass
        # print(audiofile.keys())
        audiofile['album'] = album
        audiofile['artist'] = artist
        audiofile['tracknumber'] = str(index + 1)
        audiofile['title'] = title
        audiofile.save(v2_version=3)
        audiofile = MP3(location + "{0}\{1} - {2}.mp3".format(album, artist, title), ID3=ID3)
        audiofile.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime='image/png',  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc=u'Cover',
                data=open("{0}{1}\{1}.png".format(location, album), 'rb').read()
            )
        )
        audiofile.save(v2_version=3)


def download(album):
    # album = input("enter the name of the album you want: ")
    url = search_youtube(album)
    cwd = getcwd()

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # print(info_dict.keys())
        artist = info_dict['creator']
        # if artist:
        print('The artist is {0}.'.format(artist))
        #     answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
        #     artist = answer if answer != '' else artist
        # else:
        #     artist = input('There is no artist for this album. Who is the artist? ')
        description = info_dict['description']
        title = info_dict['title']
        duration = info_dict['duration']
        length = datetime.timedelta(seconds=duration)
        tracks = search_tracks(artist, album)
        summary = album_info(artist, album)
        genres = info_dict['categories']
        cover_art = got_cover_art(artist, album)
        # print(cover_art)
        pathlib.Path("{0}/output/{1}/{2}".format(cwd, artist, album)).mkdir(parents=True, exist_ok=True)
        save_art(cover_art, '{0}\\output\\{1}\\'.format(cwd, artist), album)
        album_information = {"summary": summary, "genre": genres, "album_length": length}

        ydl_opts['outtmpl'] = '/output/{0}/{1}/%(title)s.mp3'.format(artist,album)
    # find track times (if present)
    # timestamps = find_timestamps(description)
    # print(timestamps)
    # if timestamps == []:
    timestamps = getsTimeStamps(album, artist, len(search_tracks(artist, album)))
    timestamps = times_to_stamps(timestamps)
    # print(timestamps)

    audio_location = "{0}\output\{1}\{2}\{3}.mp3".format(cwd, artist, album, title)
    # print(audio_location)

    # download album
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])

    # millitimes = convert_timestamps_to_milliseconds(timestamps)
    # albumaudio = AudioSegment.from_file(audio_location)
    # split_tracks_using_milliseconds(albumaudio,artist,album,millitimes,tracks)
    # split_tracks_intelligently(albumaudio, artist, album,millitimes, tracks)
    location = "{0}\\output\\{1}\\".format(cwd, artist)
    update_tags(location, artist, album, tracks)
    shutil.make_archive("{}\\albumzips\\{}".format(cwd,album), 'zip', "{0}\\output\\{1}\\{2}".format(cwd,artist,album))
    return "\\albumzips\\{}.zip".format(album)

# download()
