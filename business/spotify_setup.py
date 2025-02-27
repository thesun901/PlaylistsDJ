import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, dotenv_values
from typing import Optional


load_dotenv()
CLIENT_ID: Optional[str] = os.getenv('client_id')
CLIENT_SECRET: Optional[str] = os.getenv('client_secret')

sp_oauth: spotipy.SpotifyOAuth = SpotifyOAuth(
     client_id=CLIENT_ID,
     client_secret=CLIENT_SECRET,
     redirect_uri='http://localhost:3000',
     scope='user-library-read app-remote-control '
           'user-read-playback-state user-modify-playback-state '
           'user-read-currently-playing',
     show_dialog=True
 )

# import this variable to other files if you want to make spotify calls
sp: spotipy.Spotify = spotipy.Spotify(auth_manager=sp_oauth)