client_id = "ENTER_YOUR_CLIENT_ID_HERE"
client_secret = "ENTER_YOUR_CLIENT_SECRET_HERE"

import spotipy, time, os, re, youtube_dl
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from mutagen.easyid3 import EasyID3
from collections import Counter
import urllib.request

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/out"

if not os.path.exists(dir_path):
    os.makedirs(dir_path)

if len(os.listdir(dir_path)) != 0:
    exit("Out folder has to be empty!")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_link = input("Enter Spotify Playlist Link: ")
playlist_URI = playlist_link.split("/")[-1].split("?")[0]
track_uris = []
if len(playlist_URI) != 22:
    exit("Playlist was not found!")
try:
    track_uris = sp.playlist_items(playlist_URI)["items"]
except Exception:
    exit("Playlist is not public!")

infos = []
process = 1
songs_in_playlist = len(track_uris)

for track in track_uris:
    print("Creating querys: " + str(process) + "/" + str(songs_in_playlist))
    track_name = track["track"]["name"]
    artist_name = track["track"]["artists"][0]["name"]
    album_name = track["track"]["album"]["name"]
    image_url = track["track"]["album"]["images"][1]["url"]

    results = YoutubeSearch(track_name + " " + artist_name + " lyrics", max_results=1).to_dict()

    info = {"name": track_name, "artist": artist_name, "id": results[0]["id"], "album": album_name, "image": image_url}
    double = False
    for i in infos:
        if i["id"] == info["id"]:
            double = True

    if not double:
        infos.append(info)

    time.sleep(0.5)

    process += 1


def download_audio(_id, name, artist, album, url, number):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg-location': dir_path,
        'outtmpl': dir_path + "/%(id)s.%(ext)s",
        'keepvideo': 'False'
    }
    meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(_id)
    save_location = dir_path + "/" + meta['id'] + ".mp3"
    try:
        os.remove(dir_path + "/" + meta['id'] + ".webm")
    except OSError:
        pass

    try:
        os.remove(dir_path + "/" + meta['id'] + ".m4a")
    except OSError:
        pass

    audio = EasyID3(save_location)
    audio["artist"] = u"" + str(artist)
    audio['title'] = u"" + str(name)
    audio['composer'] = u"" + str(artist)
    audio["album"] = u"" + str(album)
    audio["tracknumber"] = u"" + str(number)
    audio.save()
    audio = MP3(save_location, ID3=ID3)
    urllib.request.urlretrieve(url, dir_path + "/" + meta["id"] + ".jpg")
    audio.tags.add(
        APIC(
            encoding=0,
            mime='image/jpg',
            type=3,
            desc=u'Cover',
            data=open(dir_path + "/" + meta["id"] + ".jpg", "rb").read()
        )
    )
    audio.save()
    try:
        os.remove(dir_path + "/" + meta["id"] + ".jpg")
    except OSError:
        print("could not remove image")
        pass
    rename = re.sub(r'[\\/*?:"<>|]', "", str(name))
    rename = rename[:200]
    filenames = next(os.walk(dir_path), (None, None, []))[2]
    while rename + ".mp3" in filenames:
        rename += "1"
    os.rename(save_location, dir_path + "/" + rename + ".mp3")


process = 1
songs_error = []

for i in infos:
    print("Downloading: " + str(process) + "/" + str(len(infos)))
    try:
        download_audio(_id=i["id"], name=i["name"], artist=i["artist"], album=i["album"], url=i["image"], number=process)
    except Exception:
        songs_error.append(i["id"])
        print("Error occurred. Added song to songs with error query.")
    time.sleep(10)
    process += 1

error_count = []

while len(songs_error) > 0:
    track_number = 1
    for i in infos:
        if i["id"] in songs_error:
            print("Downloading songs with error...\nSongs with errors left: " + str(len(songs_error)))
            try:
                download_audio(_id=i["id"], name=i["name"], artist=i["artist"], album=i["album"], url=i["image"], number=track_number)
                songs_error.remove(i["id"])
                while i["id"] in error_count:
                    error_count.remove(i["id"])
                print("Removed one error song: " + i["id"])
            except Exception:
                counts = Counter(error_count)
                if counts[i["id"]] > 2:
                    print("Too many errors on song: " + i["id"] + ". Removing it from query...")
                    songs_error.remove(i["id"])
                    while i["id"] in error_count:
                        error_count.remove(i["id"])
                    print("Had to remove one error song: " + i["id"])
                else:
                    error_count.append(i["id"])
                    print("Song got error again. ID of song: " + i["id"])
            time.sleep(30)
        track_number += 1

print("Done! Downloaded " + str(len(os.listdir(dir_path))) + "/" + str(len(track_uris)) + " songs!")
