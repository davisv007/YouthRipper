import wikipedia
import re
import datetime

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


def main():
    artist = "Frank Ocean"
    album3 = "Blonde"
    albumn = wikipedia.page(artist + album3)
    # print(albumn.url)
    albumn2 = albumn.html()
    # print(albumn2)

    pattern =r'[0-9]{2}:[0-9]{2}|[0-9]:[0-9]{2}' #Time stamp length #Hour:Minute:Seconds or Minute:Second or Second:Second

    p = re.compile(pattern=pattern) #compiles pattern
    x=p.findall(albumn2)
    print(x)
    stamps =  times_to_stamps(x)
    print(stamps)


main()
