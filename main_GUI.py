import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"
from spotify_setup import sp
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import StringProperty, VariableListProperty
from processing_functions import get_playlist_id_from_url
from typing import Optional
from playback_state_functions import start_new_playback, get_current_playback_state, play_pause

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '720')


PLAY_BUTTON_SRC: str = "pictures/play_button.png"
PAUSE_BUTTON_SRC: str = "pictures/pause_button.png"
UPDATE_INTERVAL_SEC: float = 0.3


class ImageButton(ButtonBehavior, Image):
    pass


class MainLayout(Screen):
    default_size: VariableListProperty = VariableListProperty()
    current_song_length: float = 10000
    current_song_timestamp: float = 5000
    current_song_name: str = "song"
    current_artist_name: str = "artist"
    is_playing: bool = False
    track_image_source: str = u"https://i.scdn.co/image/ab67616d00001e0217c960d3c483b13694bf625d"
    current_playlist_id: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.time_updater, UPDATE_INTERVAL_SEC)
        try:
            self.update_current_info()
        except:
            pass

    def set_playlist(self, playlist_id: str):
        self.current_playlist_id = playlist_id

    def update_loaded_playlist_info(self, playlist_info: Optional[dict]):
        if playlist_info:
            self.ids.playlist_image.source = playlist_info["images"][0]["url"]
            self.ids.playlist_image.color = (1, 1, 1, 1)
            self.ids.playlist_name.text = playlist_info["name"]

            first_song_of_playlist = playlist_info["tracks"]["items"][0]["track"]
            start_new_playback(song=first_song_of_playlist, context=playlist_info)
            Clock.schedule_once(lambda dt: self.update_current_info(), 1)


    def update_timebar_position(self):
        pos = self.current_song_timestamp/self.current_song_length
        if pos >= 1:
            self.update_current_info()
            return
        self.ids.time_bar.value = pos

    def update_current_info(self):
        try:
            playback_info = get_current_playback_state()
        except:
            return

        if playback_info:
            if playback_info["is_playing"]:
                self.is_playing = True
                self.ids.stop_start_button.source = PAUSE_BUTTON_SRC
            else:
                self.is_playing = False
                self.ids.stop_start_button.source = PLAY_BUTTON_SRC

            self.current_song_timestamp = playback_info['progress_ms']
            self.current_song_length = playback_info['item']['duration_ms']

            self.track_image_source = playback_info['item']['album']['images'][0]['url']
            self.ids.track_image.source = self.track_image_source

            self.current_song_name = playback_info['item']['name']
            self.current_artist_name = playback_info['item']['artists'][0]['name']
            self.ids.song_name.text = self.current_song_name
            self.ids.artist_name.text = self.current_artist_name

            self.update_timebar_position()
        else:
            self.current_song_timestamp = self.current_song_length

    def play_pause(self, widget):
        try:
            self.is_playing = play_pause()
        except:
            return

        if self.is_playing:
            widget.source = PLAY_BUTTON_SRC
        else:
            widget.source = PAUSE_BUTTON_SRC

        Clock.schedule_once(lambda dt: self.update_current_info(), 1)

    def next_song(self):
        sp.next_track()
        Clock.schedule_once(lambda dt: self.update_current_info(), 1)

    def previous_song(self):
        try:
            sp.previous_track()
        except:
            playback_info = get_current_playback_state()
            if playback_info['context'] is None:
                sp.start_playback(uris=[playback_info['item']['uri']], position_ms=0)
            else:
                sp.start_playback(context_uri=playback_info['context']['uri'], offset={"uri": playback_info['item']['uri']}, position_ms=0)
        Clock.schedule_once(lambda dt: self.update_current_info(), 1.5)


    def change_song_moment(self, touch, widget):
        if touch.grab_current == widget:
            playback_info = get_current_playback_state()
            new_position: int = int(widget.value * self.current_song_length)
            self.current_song_timestamp = new_position
            start_new_playback(playback_info['item'], playback_info['context'], position=new_position)


    def time_updater(self, dt):
        if self.is_playing:
            self.current_song_timestamp = self.current_song_timestamp + UPDATE_INTERVAL_SEC*1000
            self.update_timebar_position()

    def click_animate(self, widget, *args):
        beggining_size = widget.default_size
        anim = Animation(
            size_hint=(widget.size_hint_x * 1.1, widget.size_hint_y * 1.1),
            duration=0.1
        )
        anim += Animation(
            size_hint=beggining_size,
            duration=0.1
        )
        anim.start(widget)


class OnePointSearchLayout(Screen):
    pass


class PlaylistPopup(Popup):
    current_playlist_id: Optional[str] = None
    root_widget: Optional[MainLayout] = None
    playlist_info: Optional[dict] = None
    playlist_image_source: Optional[str] = None

    def __init__(self, root_widget: Screen, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = root_widget

    def load_playlist(self):
        self.current_playlist_id = get_playlist_id_from_url(self.ids.playlist_link.text)
        try:
            playlist = sp.playlist(playlist_id=self.current_playlist_id)
            self.playlist_info = playlist
            self.ids.popup_playlist_image.color = (1, 1, 1, 1)
            self.ids.popup_playlist_image.source = playlist["images"][0]["url"]
            self.ids.playlist_name_popup.text = playlist["name"]
            self.ids.tracks_number_popup.text = f"number of tracks: " + str(playlist["tracks"]["total"])
        except:
            self.ids.popup_playlist_image.color = (1, 1, 1, 0)
            self.ids.popup_playlist_image.source = ""
            self.ids.playlist_name_popup.text = ""
            self.ids.tracks_number_popup.text = ""

    def set_root_playlist(self):
        self.root_widget.set_playlist(self.current_playlist_id)
        self.root_widget.update_loaded_playlist_info(self.playlist_info)

class MainApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MainApp().run()
