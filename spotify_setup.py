import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, dotenv_values


load_dotenv()
CLIENT_ID = os.getenv('client_id')
CLIENT_SECRET = os.getenv('client_secret')

sp_oauth = SpotifyOAuth(
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET,
     redirect_uri='http://localhost:3000',
     scope='user-library-read app-remote-control '
           'user-read-playback-state user-modify-playback-state '
           'user-read-currently-playing',
     show_dialog=True
 )


sp = spotipy.Spotify(auth_manager=sp_oauth)