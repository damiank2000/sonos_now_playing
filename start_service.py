import soco
import pylast
import json
import logging
import os
from time import sleep
from papirus import Papirus
from papirus import PapirusText


class LastFmConfig:
    'Sonos now playing config class'

    def __init__(self, config_root):
        self.lastfm_config = config_root['last.fm']
        self.API_KEY = self.lastfm_config['api_key']
        self.API_SECRET = self.lastfm_config['api_secret']
        self.username = self.lastfm_config['username']
        self.password_hash = pylast.md5(self.lastfm_config['password'])


def display_transport_info(player):
    transport = player.get_current_transport_info()
    for x, y in transport.items():
        print(x + " " + y)


def display_now_playing(now_playing):
    text.write(now_playing)
    logging.info(now_playing)


def get_sonos_title(track):
    return "{} by {}".format(track['title'].encode('utf-8'), track['artist'].encode('utf-8'))


def get_lastfm_title(track, default):
    if track is not None:
        title = "{} by {}".format(track.title.encode('utf-8'), track.artist.name.encode('utf-8'))
    else:
        title = default
    return title


def get_6music_title():
    current_track = user.get_now_playing()
    if current_track is not None:
        current_6music_title = get_lastfm_title(current_track, default_6music_text)
    else:
        current_6music_title = default_6music_text
    return current_6music_title


def get_transport_status(player):
    transport = player.get_current_transport_info()
    return transport['current_transport_state']


def get_current_title(player):
    track = player.get_current_track_info()
    title = track['title']
    if title == "bbc_6music.m3u8":
        title = get_6music_title()
    else:
        title = get_sonos_title(track)
    return title


def get_lastfm_user(lastfm_config):
    network = pylast.LastFMNetwork(
        api_key=lastfm_config.API_KEY,
        api_secret=lastfm_config.API_SECRET,
        username=lastfm_config.username,
        password_hash=lastfm_config.password_hash)
    return network.get_user('bbc6music')

# start
logging.basicConfig(
    filename='sonos_now_playing.log',
    level=logging.WARNING,
    format='%(asctime)s %(message)s')

config_file_location=os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(config_file_location, 'sonos_now_playing_config.json')) as json_data_file:
    config = json.load(json_data_file)

zone_of_interest=config['sonos']['zone_of_interest']
user = get_lastfm_user(LastFmConfig(config))
screen = Papirus()
text = PapirusText()
last_playing="None"
default_6music_text="BBC 6 Music"

screen.clear()
text.write("Starting")
logging.info("Monitoring zone: {}".format(zone_of_interest))

while True:
    try:
        for zone in soco.discover():
            if zone.player_name == zone_of_interest:
                status = get_transport_status(zone)
                if status == "PLAYING":
                    current_title = get_current_title(zone)
                else:
                    current_title = ""
                if current_title != last_playing:
                    last_playing = current_title
                    display_now_playing(last_playing)

                sleep(1)
    except KeyboardInterrupt:
        print("Exit")
	screen.clear()
        break
    except (ValueError, IndexError, KeyError, IOError, SystemError) as ex:
        logging.error(ex)
	screen.clear()
        raise

