import datetime  # date and time stamp
import re  # regular expression module used for searching patterns
from urllib.parse import quote

import requests
import wikipedia
import youtube_dl  # downloads youtube via links
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import EasyMP3 as MP3
from pydub import silence

from config import *


def fix_filename(string):
    valid_file_name = re.sub('[^\w_.)( -]', '', string.replace(' ', '_'))


def song_lengths_to_timesstamps(x):
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


def get_tracks_from_lastfm(artist, album):
    album_tracks = pylast.Album(artist, album, network)
    tracks = album_tracks.get_tracks()
    tracks = [str(track).split('- ')[1] for track in tracks]
    return tracks


def get_cover_art(artist, album):
    art = pylast.Album(artist, album, network)
    cover_art = art.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
    return cover_art


def get_youtube_time_stamps(description):
    pattern = r'[0-2]{2}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern)  # compiles pattern
    timestamps = p.findall(description)
    # if sum(timestamps[0].split(':')) == {0}:  #trying to find out if the timestamp is all zeroes
    #     timestamps = timestamps[1:]
    return timestamps


def timestamps_to_milliseconds(timestamps):
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


def split_tracks_using_milliseconds(audio, artist, album, timelist, tracks):
    for i in range(len(timelist) - 1):
        track = audio[timelist[i]:timelist[i + 1]]
        track.export(out_f=ALBUMSLOCATION + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[i]),
                     format='mp3',
                     bitrate="320k")
    track = audio[timelist[-1]:]
    track.export(out_f=ALBUMSLOCATION + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[-1]),
                 format='mp3', bitrate="320k")


def split_tracks_by_silence(audio, artist, album, timelist, tracks):
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
        track.export(out_f=ALBUMSLOCATION + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[i]),
                     format='mp3',
                     bitrate="320k")
    track = audio[new_timelist[-1]:]
    track.export(out_f=ALBUMSLOCATION + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[-1]),
                 format='mp3', bitrate="320k")


def search_youtube(album):
    textToSearch = '{} {}'.format(album, 'full album')
    query = quote(textToSearch)
    url = "https://www.youtube.com/results?search_query={}".format(query)
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    link_list = ['{}{}'.format('https://www.youtube.com', vid['href'])
                 for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'})]
    link_list = [link for link in link_list if len(link) == 43]
    return link_list[0]


# Gathers the time stamps of any album and displays in list of strings
def get_song_lengths_from_wiki(albumName, albumArtist, maxlen=None):
    albumInfo = wikipedia.page(albumName + ' ' + albumArtist)  # searches all wikipedia pages
    # print(albumInfo)
    print(' ')
    if albumInfo == False:
        albumInfo = wikipedia.page(albumArtist + ' ' + albumName)
        albumInfoHtml = albumInfo.html()
    else:
        albumInfoHtml = albumInfo.html()  # displays every listing on html plage

    soup = BeautifulSoup(albumInfoHtml, 'html.parser')
    print(soup.text)  # ('div', attrs={'class': 'container'}).text)
    # print(soup.prettify())
    # x= soup.find_all('table')
    # print(x)
    pattern = r'[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second

    p = re.compile(pattern=pattern)  # compiles pattern
    timeStamps = p.findall(albumInfoHtml)
    # print(timeStamps)
    if maxlen is not None:
        return timeStamps[:maxlen]
    else:
        return timeStamps


def save_art(artwork_link, location, album):
    with open('{0}{1}\\{2}.png'.format(location, album, album), 'wb') as f:
        f.write(requests.get(artwork_link).content)
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


def download(album, artist):
    url = search_youtube(album)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # description = info_dict['description']
        # tracks = get_tracks_from_lastfm(artist, album)
        # cover_art = get_cover_art(artist, album)
        print('Url:{} Artist:{} Album:{}.'.format(url, artist, artist))
    #     pathlib.Path(path.join(ALBUMSLOCATION, artist, album)).mkdir(parents=True, exist_ok=True)
    #     pathlib.Path(path.join(ALBUMSLOCATION, artist, album, album)).mkdir(parents=True, exist_ok=True)
    #     save_art(cover_art, path.join(ALBUMSLOCATION, artist), album)
    #     ydl_opts['outtmpl'] = path.join('output', artist, album, '%(title)s.mp3')
    #
    # # find track times (if present)
    # # timestamps = get_youtube_time_stamps(description)
    # # print(timestamps)
    # # if timestamps == []:
    # songlengths = get_song_lengths_from_wiki(album, artist)
    # timestamps = song_lengths_to_timesstamps(songlengths)
    # print(len(timestamps))
    # print(len(tracks))
    #
    # # download album
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #     ydl.download([url])
    #
    # # load audio into memory
    # audio_location = path.join(ALBUMSLOCATION, artist, album, title, '.mp3')
    # albumaudio = AudioSegment.from_file(audio_location)
    #
    # # convert list of time stamps into milliseconds
    # millitimes = timestamps_to_milliseconds(timestamps)
    # split_tracks_using_milliseconds(albumaudio, artist, album, millitimes, tracks)
    # # split_tracks_by_silence(albumaudio, artist, album,millitimes, tracks)
    #
    # # add tags
    # location = path.join(ALBUMSLOCATION, artist)
    # update_tags(location, artist, album, tracks)
    #
    # # make
    # shutil.make_archive(path.join(ZIPLOCATION, album), 'zip', path.join(ALBUMSLOCATION, artist, album, album))
    # return path.join('albumzips', album, '.zip')


if __name__ == '__main__':
    download(input("enter the name of the album you want: "))
