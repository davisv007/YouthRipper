import wikipedia
import re
import datetime


def times_to_stamps(x):
    times = [list(reversed(time.split(':'))) for time in x]
    new_times = []
    for time in times:
        new_time = 0
        for index, unit in enumerate(time):
            new_time += int(unit) * (60 ** index)
        new_times.append(new_time)
    newer_time = [0]
    for index, time in enumerate(new_times):
        newer_time.append(str(datetime.timedelta(seconds=time + sum(new_times[:index]))))
    return newer_time


def main():
    artist = "Frank Ocean"
    album3 = "Blonde"
    album = wikipedia.page(artist + album3)
    # print(album.url)
    album2 = album.section('Track listing')
    # album2=album2.split('\n')

    print(album2)
    tracknamepattern=r'"(.*?)"'
    # timestamppattern = r'[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}'  # Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second
    # tp = re.compile(pattern=tracknamepattern)  # compiles pattern
    # tracklist=[]
    # for line in album2:
    #     tracks=tp.findall(line)
    #     if len(tracks)>0:
    #         tracklist.append(tracks[0])
    #
    # print(tracklist)
    # p = re.compile(pattern=pattern)  # compiles pattern
    # x = p.findall(album2)
    # print(x)
    # stamps = times_to_stamps(x)
    # print(stamps)


main()
