# youtube timecode audio splitter
Download music video and split into separate audio files using timecodes.


usage: main.py [-h] [-r REGEX] [-f FORMAT] [-b BITRATE] url

Download music video and split into separate audio files using timecodes

positional arguments:
  url                   Url to youtube video

optional arguments:
  -h, --help            show this help message and exit
  -r REGEX, --regex REGEX
                        Use this regex to parse description for timecodes.
                        Regex should use named groups, and at least <track> and <time> groups should be present
                        Example 1:
                            [1:02:20] Super Castlevania IV, "The Library"
                            (?P<track>\[(?P<time>[\d\:]*)\]\s*(?P<album>.*),\s*"(?P<title>.*)")
                        Example 2:
                            0:00 - João Gilberto, Solidão
                            (?P<track>(?P<time>[\d\:]*)\s* - \s*(?P<artist>.*),\s*(?P<title>.*))
                        Please refer to regex tutorials at https://regex101.com
  -f FORMAT, --format FORMAT
                        output format [mp3, ogg, etc]
  -b BITRATE, --bitrate BITRATE
                        output bitrate [192, 320, etc]
                        
                        
