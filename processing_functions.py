from spotify_setup import sp
from typing import Optional, Match
import re


def get_playlist_id_from_url(url: str) -> Optional[str]:
    match: Optional[Match[str]] = re.search(r"playlist/([a-zA-Z0-9]+)(\?|$)", url)
    if match:
        return match.group(1)
    else:
        return None


def get_audio_features(tracks: list[dict]) -> Optional[list[dict]]:
    tracks_id = []
    for item in tracks:
        tracks_id.append(item['track']['id'])
    features_list: list[dict] = []

    # api call has limit of 100 songs - getting all song features from playlist
    while len(tracks_id) > 0:
        try:
            result = sp.audio_features(tracks=tracks_id[:100])
            features_list.extend(result)
            tracks_id = tracks_id[100:] if len(tracks_id) > 100 else []

        except Exception as e:
            print(e)
            return None

    return features_list


def get_all_tracks(playlist_id: str) -> Optional[list]:
    tracks = None
    try:
        results = sp.playlist_items(playlist_id=playlist_id)
        tracks = results['items']

        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    except Exception as e:
        print(e)

    return tracks


