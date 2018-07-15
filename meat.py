import pathlib
import re  # regular expression module used for searching patterns
import shutil
from datetime import timedelta
from urllib.parse import quote

import requests
import wikipedia
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3 as MP3
from pydub import silence, AudioSegment
from pytube import YouTube

from config import *


def seconds_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{}:{}:{}".format(h, m, s)


def get_info(url):
    # pytube is installed from latest source on their github: https://github.com/nficano/pytube
    yt = YouTube(url)
    duration = seconds_hms(int(yt.length))
    title = yt.title
    page_html = yt.watch_html
    soup = bs(page_html, "html.parser")
    description_html = soup.find("p", attrs={"id": "eow-description"})
    description = bs(str(description_html).replace('<br/>', '\n<br/>'), "html.parser").text

    return title, duration, description


def fix_filename(string):
    return re.sub('[^\w_.)( -]', '', string.replace(' ', '_'))


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
        newer_time.append(str(timedelta(seconds=time + sum(new_times[:index]))))
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
    pattern = r'\d{0,2}:?\d{1,2}:\d{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern)  # compiles pattern
    timestamps = p.findall(description)
    # if sum(timestamps[0].split(':')) == {0}:  #trying to find out if the timestamp is all zeroes
    #     timestamps = timestamps[1:]
    if timestamps == []:
        return None
    else:
        return timestamps


def get_youtube_tracks(description):
    pattern = r'(?:\d{0,2}:?\d{1,2}:\d{2})(.*)'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    p = re.compile(pattern=pattern)  # compiles pattern
    tracklist = p.findall(description)
    # from each track, remove the timestamp
    pattern = r'\d{2}:\d{2}:\d{2}|\d{2}:\d{2}|\d{1}:\d{2}|\d{1}:\d{2}:\d{2}'
    tracklist = [re.sub(pattern, '', track) for track in tracklist]
    return tracklist


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


def split_tracks_using_milliseconds(audio, artist, album, timelist, track_dict):
    for i, ele in enumerate(list(track_dict.keys())):
        track = audio[timelist[i]:timelist[i + 1]]
        track.export(out_f=path.join(SPLITALBUMSLOC, artist, album, track_dict[ele] + ".mp3"),
                     format='mp3',
                     bitrate="320k")


def split_tracks_by_silence(audio, artist, album, timelist, tracks):
    cwd = getcwd()
    tolerance = 1500  # 3 seconds
    new_timelist = [timelist[0]]

    for i in range(1, len(timelist)):
        track = audio.get_sample_slice(timelist[i] - tolerance, timelist[i] + tolerance)
        x = silence.detect_silence(track, silence_thresh=track.dBFS, min_silence_len=10)[0]
        new_timestamp = timelist[i] - tolerance + (sum(x) / len(x)) + 2000
        new_timelist.append(new_timestamp)
        print(timedelta(seconds=new_timestamp / 1000))

    for i in range(len(new_timelist) - 1):
        track = audio[new_timelist[i]:new_timelist[i + 1]]
        track.export(out_f=FULLALBUMSLOC + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[i]),
                     format='mp3',
                     bitrate="320k")
    track = audio[new_timelist[-1]:]
    track.export(out_f=FULLALBUMSLOC + "{0}\{1}\{1}\{2}.mp3".format(artist, album, artist + ' - ' + tracks[-1]),
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


def save_art(artwork_link, location):
    with open(path.join(location, 'cover.png'), 'wb') as f:
        f.write(requests.get(artwork_link).content)
        f.close()


def update_tags(artist, album, track_dict):
    # edit the ID3 tag to add the title, artist, artwork, date, and genre
    for index, title in enumerate(list(track_dict.keys())):
        # print(location+"{}.mp3".format(title))
        # break
        audiofile = MP3(path.join(SPLITALBUMSLOC, artist, album, track_dict[title] + '.mp3'))
        # try:
        #     audiofile.add_tags()
        # except error:
        #     pass
        # print(audiofile.keys())
        audiofile['album'] = album
        audiofile['artist'] = artist
        audiofile['tracknumber'] = str(index + 1)
        audiofile['title'] = title
        audiofile.save(v2_version=3)
        audiofile = MP3(path.join(SPLITALBUMSLOC, artist, album, track_dict[title] + '.mp3'), ID3=ID3)
        audiofile.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime='image/png',  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc=u'Cover',
                data=open(path.join(SPLITALBUMSLOC, artist, album, 'cover.png'), 'rb').read()
            )
        )
        # audiofile.save()
        audiofile.save(v2_version=3)


def download(album, artist):
    album_filename = fix_filename(album)
    pathlib.Path(path.join(FULLALBUMSLOC, artist, album_filename)).mkdir(parents=True, exist_ok=True)
    pathlib.Path(path.join(SPLITALBUMSLOC, artist, album_filename)).mkdir(parents=True, exist_ok=True)
    pathlib.Path(path.join(ZIPLOCATION, artist, album_filename)).mkdir(parents=True, exist_ok=True)

    # get link to video
    url = search_youtube(album)

    # get title, duration, description
    title, duration, description = get_info(url)

    # get timestamps from description
    timestamps = get_youtube_time_stamps(description)
    timestamps.append(duration)

    # find track times (if present)
    tracks = get_youtube_tracks(description)
    track_filenames = [fix_filename(track) for track in tracks]
    track_dict = {track: filename for track, filename in zip(tracks, track_filenames)}

    print('Url:{} Artist:{} Album:{}.'.format(url, artist, album))
    # print(title)
    # print(description)
    # print(duration)
    # print(tracks)
    # print(timestamps)

    # get cover art, save it
    cover_art = get_cover_art(artist, album)
    save_art(cover_art, path.join(SPLITALBUMSLOC, artist, album))

    # load audio into memory
    audio_location = path.join(FULLALBUMSLOC, artist, album, title + '.mp3')
    albumaudio = AudioSegment.from_file(audio_location)

    # convert list of time stamps into milliseconds
    millitimes = timestamps_to_milliseconds(timestamps)
    split_tracks_using_milliseconds(albumaudio, artist, album, millitimes, track_dict)

    # add tags
    update_tags(artist, album, track_dict)

    # make zip file
    shutil.make_archive(path.join(ZIPLOCATION, artist, album), 'zip', path.join(SPLITALBUMSLOC, artist, album))
    return path.join('albumzips', artist, album + '.zip')
