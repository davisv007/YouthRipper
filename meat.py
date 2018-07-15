import datetime  # date and time stamp
import pathlib
import re  # regular expression module used for searching patterns
import shutil
import time
from urllib.parse import quote

import requests
import wikipedia
import youtube_dl  # downloads youtube via links
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3 as MP3
from pydub import silence, AudioSegment
from selenium.webdriver import Chrome, ChromeOptions

from config import *

from pytube import YouTube


def get_info(url):
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = Chrome(chrome_options=chrome_options)
    driver.get(url)
    time.sleep(2)
    duration = driver.find_element_by_xpath(
        "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch/div[2]/div[1]/div[1]/div/div[21]/div[2]/div[1]/div/span[3]").text
    description = driver.find_element_by_xpath('//*[@id="description"]').get_attribute("innerText")
    driver.quit()
    return duration, description


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
        print(datetime.timedelta(seconds=new_timestamp / 1000))

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

    url = search_youtube(album)
    print('Url:{} Artist:{} Album:{}.'.format(url, artist, album))

    ydl_opts['outtmpl'] = path.join(FULLALBUMSLOC, artist, album_filename, '%(title)s.mp3')

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict['title']
        # ydl.download([url])
    duration, description = get_info(url)
    # print(info_dict)
    # print(title)
    # print(description)
    # print(duration)

    # find track times (if present)
    timestamps = get_youtube_time_stamps(description)
    timestamps.append(duration)
    # if timestamps == []:
    #     songlengths = get_song_lengths_from_wiki(album, artist)
    #     timestamps = song_lengths_to_timesstamps(songlengths)
    # tracks = get_tracks_from_lastfm(artist, album)

    tracks = get_youtube_tracks(description)
    track_filenames = [fix_filename(track) for track in tracks]
    track_dict = {track: filename for track, filename in zip(tracks, track_filenames)}

    # print(tracks)
    # print(timestamps)
    # print(path.exists(path.join(FULLALBUMSLOC, artist, album_filename, title+'.mp3')))

    cover_art = get_cover_art(artist, album)
    save_art(cover_art, path.join(SPLITALBUMSLOC, artist, album))

    # load audio into memory
    audio_location = path.join(FULLALBUMSLOC, artist, album, title + '.mp3')
    albumaudio = AudioSegment.from_file(audio_location)

    # convert list of time stamps into milliseconds
    millitimes = timestamps_to_milliseconds(timestamps)
    split_tracks_using_milliseconds(albumaudio, artist, album, millitimes, track_dict)
    # split_tracks_by_silence(albumaudio, artist, album,millitimes, tracks)

    # add tags
    # location = path.join(FULLALBUMSLOC, artist)
    update_tags(artist, album, track_dict)

    # make
    shutil.make_archive(path.join(ZIPLOCATION, artist, album), 'zip', path.join(SPLITALBUMSLOC, artist, album))
    return path.join('albumzips', artist, album + '.zip')

# if __name__ == '__main__':
# #     download(input("enter the name of the album you want: "))
