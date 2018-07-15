from os import getcwd, path

import pylast

API_KEY = "a0472e3ba14a8c6b2d373f25f7214f47"
API_SECRET = "e3706cbf68860e14e3da9bf6968b66c4"
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
FULLALBUMSLOC = path.join(getcwd(), 'output')
ZIPLOCATION = path.join(getcwd(), 'albumzips')
SPLITALBUMSLOC = path.join(getcwd(), 'albums')


# Determines when video is done converting
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


# MyLogger uses the Logger module to display error logs
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


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
