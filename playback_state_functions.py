from spotify_setup import sp
from typing import Optional, Match


def start_new_playback(song: dict, context: Optional[dict] = None, position: int = 0):
    try:
        if context is None:
            sp.start_playback(uris=[song['uri']], position_ms=position)
        else:
            sp.start_playback(context_uri=context['uri'], offset={"uri": song['uri']}, position_ms=position)
    except:
        pass


def get_current_playback_state() -> Optional[dict]:
    return sp.current_playback()


def play_pause() -> bool:
    """Resumes playback on pause, stops playback if is playing.
    Returns True if started playback and False if stopped """
    playback_info = get_current_playback_state()
    if playback_info is not None:
        state = playback_info["is_playing"]
        if state:
            sp.pause_playback()
            return False
        else:
            sp.start_playback()
            return True

