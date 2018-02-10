from __future__ import unicode_literals
import youtube_dl
import datetime

# hdhfhf
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


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

    url ="https://www.youtube.com/watch?v=4o5baMYWdtQ"
    # url = "https://www.youtube.com/watch?v=-tT32VTll5M"
    # url = "https://www.youtube.com/watch?v=FUXX55WqYZs"
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # print(info_dict.keys())
        artist = info_dict['creator']
        description = info_dict['description']
        title = info_dict['title']
        length =datetime.timedelta(seconds= info_dict['duration'])
        # print(artist)
        # print(description)
        # print(title)
        print(length)

        # if artist:
        #     print('The artist is {0}.'.format(artist))
        #     answer = input('If this is correct, press enter, otherwise enter the correct artist: ')
        #     artist = answer if answer != '' else artist
        # else:
        #     artist = input('There is no artist for this album. Who is the artist? ')
        # ydl_opts['outtmpl']='/output/{0}/%(title)s'.format(artist)
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
