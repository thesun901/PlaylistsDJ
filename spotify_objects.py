

class Track:
    def __init__(self, song_dict: dict):
        self.id = song_dict['id']


class Playlist:
    def __init__(self, playlist_dict: dict):
        self.id: str = playlist_dict['id']
        self.name: str = playlist_dict['name']
        self.image: str = playlist_dict['images'][0]['url']
