import youtube_dl
from googleapiclient.discovery import build
import sys
import os
import tempfile
import argparse
from pydub import AudioSegment, MyAudioSegment
import re
import time
from goldfinch import validFileName as vfn

output_mp3 = ""

class MyLogger(object):
    def debug(self, msg):
        global output_mp3
        try:
            match = re.match(".*Destination:\s*(.*\..*)", msg)
            if match:
                output_mp3 = match.group(1)
        except Exception as e:
            print(e)

    def warning(self, msg):
        print(f"W: {msg}")

    def error(self, msg):
        print(f"E: {msg}")

def my_hook(d):
    if d['status'] == 'finished':
        
        print('Done downloading, now converting ...')


def_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    "dump_single_json": False,
}

def get_meta(link, regex):
    DEVELOPER_KEY = 'AIzaSyBtMRXtzsKe5p-zwvDdhEpstxehs-_YgnQ'
    youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
    ids = link.split('=')[-1]
    results = youtube.videos().list(id=ids, part='snippet').execute()
    meta = {}
    for result in results.get('items', []):
        meta["id"] = result['id']
        meta["artist"] = "Unknown Artist"
        meta["album"] = result["snippet"]["title"]
        description = result['snippet']['description']

        pattern = re.compile(regex)
        track_data = [x.groupdict() for x in  pattern.finditer(description)]
        tracks = []
        trackno = 0
        for track in track_data:
            trackno += 1
            if 'time' not in track.keys() or not track['time']:
                print(f"Can't find timetag for {track['track']}")
                continue
                
            if 'title' not in track.keys() or not track['title']:
                track['title'] = f"Track #{trackno}"

            if 'album' not in track.keys() or not track['album']:
                track['album'] = meta['album']
            
            if 'artist' not in track.keys() or not track['artist']:
                track['artist'] = meta['artist']

            if 'comments' not in track.keys() or not track['comments']:
                track['comments'] = ''

            track['no'] = trackno

            times = re.match("((?P<hours>\d+)\:)?(?P<minutes>\d+)\:(?P<seconds>\d+)", track['time']).groupdict()
            track['time'] = 0
            try:
                if times['hours']:
                    track['time'] += int(times['hours']) * 60 * 60
                if times['minutes']:
                    track['time'] += int(times['minutes']) * 60
                if times['seconds']:
                    track['time'] += int(times['seconds'])
                track['time'] *= 1000
            except:
                print("cant parse time", track['track'])
                continue
            
            tracks.append(track)
        meta["tracks"] = tracks
        return meta
        

def download(link):

    with youtube_dl.YoutubeDL(def_opts) as ydl:
        ydl.download([link])
        return output_mp3

def format_filename(track_data, format):
    filename = f"{track_data['no']}. {track_data['artist']} [{track_data['album']}] - {track_data['title']}.{format}"
    return vfn(filename, initCap=False, ascii=False, space='keep').decode('utf-8')

def make_tags(track_data):
    tags = {'artist' : track_data['artist'],
            'album' : track_data['album'],
            'title' : track_data['title'],
            'tracknumber' : track_data['no'],
            'comments' : track_data['comments'] }
    return tags

def split(filename, meta):
    audio_file = AudioSegment.from_file(filename)
    format = filename.split('.')[-1]
    format = "mp3"
    
    for i in range(len(meta['tracks']) - 1):
        track_data = meta['tracks'][i]
        track = audio_file[track_data['time']:meta['tracks'][i+1]['time']]
        track.export(format_filename(track_data, format), tags=make_tags(track_data))
        
    
    track_data = meta['tracks'][-1]
    track = audio_file[track_data['time']:]

    track.export(format_filename(track_data, format), tags=make_tags(track_data))
    


if __name__ == "__main__":

    def_regex = r"(?P<track>(?P<time>[\d\:]*)\s*-\s*(?P<artist>.*),\s*(?P<title>.*))"

    parser = argparse.ArgumentParser(description='Download music video and split into separate audio files using timecodes',
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('URL', metavar='url', type=str, nargs=1,
                        help='Url to youtube video')
    parser.add_argument('-r', '--regex', dest='regex', action='store', default=def_regex, type=str,
                        help="""Use this regex to parse description for timecodes.
Regex should use named groups, and at least <track> and <time> groups should be present
Example 1:
    [1:02:20] Super Castlevania IV, "The Library"
    (?P<track>\[(?P<time>[\d\:]*)\]\s*(?P<album>.*),\s*\"(?P<title>.*)\")
Example 2:
    0:00 - João Gilberto, Solidão
    (?P<track>(?P<time>[\d\:]*)\s* - \s*(?P<artist>.*),\s*(?P<title>.*))
Please refer to regex tutorials at https://regex101.com""")
    parser.add_argument('-f', '--format', help='output format [mp3, ogg, etc]', action='store', default='mp3', type=str)
    parser.add_argument('-b', '--bitrate', help='output bitrate [192, 320, etc]', action='store', default='192', type=int)
    

    args = parser.parse_args()

    meta = get_meta(args.URL[0], args.regex)
    print("tracks found:")
    for track in meta['tracks']:
        print(track['track'])
    if not meta['tracks']:
        print("Failed to find any tracks in this video")
        exit(0)
    print("Downloading video ...")
    mp3_filename = download(args.URL[0])
    print("Done converting, now splitting into separate tracks ...")
    split(mp3_filename, meta)
