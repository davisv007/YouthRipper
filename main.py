from __future__ import unicode_literals
import youtube_dl


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
url ="https://www.youtube.com/watch?v=4o5baMYWdtQ"
# url="https://www.youtube.com/watch?v=FUXX55WqYZs"
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # ydl.download([url])
    info_dict = ydl.extract_info(url, download=False)
    # print(info_dict)
    print(info_dict['creator'])
    print(info_dict.keys())