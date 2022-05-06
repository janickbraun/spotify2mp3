# spotify2mp3 🎵→💾
Python script to convert Spotify playlists to mp3 files

## How to use:
- First of all you have to create a new Spotify developer application: [Click here](https://developer.spotify.com/dashboard)
- When you created it, you have to copy the client ID and the client secret of your Spotify developer application
- After that, you will have to edit the first and second line of the "main.py" file and paste your client ID and client secret
- Make sure there is no directory called "out" in the directory where the "main.py" file is located because the script will create the .mp3 files in the "out" directory
- Now you can finally execute the "main.py" file
- After you started the script the console will pop up, and you will have to enter the link of your Spotify playlist but make sure the playlist is public
- The moment you press enter, the playlist will start downloading
- It may take some time for all the tracks to download, so please be patient
- Sometimes a track will not download because of YouTube, but this is really, really rare
- Sometimes a wrong track will be downloaded, but this happens maybe in 1 in 100 downloads, so it is still a rare error
- The console will tell you what is currently going on with the downloads and even tells you how many songs are left to download
- While the script is running, do not modify the "out" directory or the files in it
- Hopefully everything works fine for you and if you liked it please feel free to give me a Starr on this repository

## How it works:
As soon as you enter the link of the Spotify playlist, all information of the tracks will be saved. Like the title, the artist name, the album and even the album cover. All this information then later will be added to the .mp3 files meta tags.
After all the information is saved, every song will be searched for on YouTube. But with the keyword lyrics at the end, so the script will not download the audio of the music video. The video will then be downloaded and converted to .mp3.
