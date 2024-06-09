from spotify_setup import sp
from typing import Optional
import re

def get_playlist_id_from_url(url: str) -> Optional[str]:
    match = re.search(r'playlist/([a-zA-Z0-9]+)(\?|$)', url)
    if match:
        return match.group(1)
    else:
        return None


def get_audio_features(track_id: str) -> Optional[dict]:
    features = None
    try:
        features = sp.audio_features(track_id)[0]
        print(type(features))

    except Exception as e:
        print(e)

    return features


def get_all_tracks(playlist_id: str, user_id: str) -> Optional[list]:
    tracks = None
    try:
        results = sp.user_playlist_tracks(playlist_id=playlist_id, user=user_id)
        tracks = results['items']

        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    except Exception as e:
        print(e)

    return tracks


def get_current_playback_state() -> Optional[dict]:
    try:
        return sp.current_playback()

    except:
        return None


