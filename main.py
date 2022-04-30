import spotipy, time, os ,re, youtube_dl
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from mutagen.easyid3 import EasyID3

if not os.path.exists("out"):
    os.makedirs("out")

if len(os.listdir("out")) != 0:
    exit("Out folder has to be empty!")


client_credentials_manager = SpotifyClientCredentials(client_id="yourclientid", client_secret="yoursecret")
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

    results = YoutubeSearch(track_name + " " + artist_name + " lyrics", max_results=1).to_dict()

    info = {"name": track_name, "artist": artist_name, "id": results[0]["id"]}
    double = False
    for i in infos:
        if i["id"] == info["id"]:
            double = True

    if not double:
        infos.append(info)

    process += 1

def download_audio(_id, name, artist):
   ydl_opts = {
       'format': 'bestaudio/best',
       'postprocessors': [{
           'key': 'FFmpegExtractAudio',
           'preferredcodec': 'mp3',
           'preferredquality': '192',
       }],
       'ffmpeg-location': './out',
       'outtmpl': "./out/%(id)s.%(ext)s",
       'keepvideo': 'False'
   }
   meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(_id)
   save_location = "./out/" + meta['id'] + ".mp3"
   try:
       os.remove("./out/" + meta['id'] + ".webm")
   except OSError:
       pass

   try:
       os.remove("./out/" + meta['id'] + ".m4a")
   except OSError:
       pass

   audio = EasyID3(save_location)
   audio["artist"] = u"" + str(artist)
   audio['title'] = u"" + str(name)
   audio['composer'] = u"" + str(artist)
   audio.save()
   rename = re.sub(r'[\\/*?:"<>|]', "", str(name))
   rename = rename[:255]
   filenames = next(os.walk("./out"), (None, None, []))[2]
   while rename + ".mp3" in filenames:
       rename += "1"
   os.rename(save_location, "./out/" + rename + ".mp3")

process = 1

songs_error = []

for i in infos:
    print("Downloading: " + str(process) + "/" + str(len(infos)))
    try:
        download_audio(_id=i["id"], name=i["name"], artist=i["artist"])
    except Exception:
        songs_error.append(i["id"])
        print("Error occurred. Added Song to Songs with error query.")
    time.sleep(10)
    process += 1

while len(songs_error) > 0:
    for i in infos:
        if i["id"] in songs_error:
            print("Downloading songs with error...\nSongs with errors left: " + str(len(songs_error)))
            try:
                download_audio(_id=i["id"], name=i["name"], artist=i["artist"])
                songs_error.remove(i["id"])
                print("Removed one error song.")
            except Exception:
                print("Song got error again. ID of song: " + i["id"])
            time.sleep(30)
