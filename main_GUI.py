import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"
from spotify_setup import sp
from kivy.app import App
from kivy.uix.behaviors.drag import DragBehavior
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.image import Image, AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import math
from kivy.uix.label import Label
import processing_functions
from kivy.config import Config
from kivy.properties import StringProperty, VariableListProperty
from processing_functions import get_current_playback_state


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.time_updater, UPDATE_INTERVAL_SEC)
        try:
            self.update_current_info()
        except:
            pass

    def btn(self):
        results = sp.current_user_saved_tracks()
        print(results)
        for idx, item in enumerate(results['items']):
            track = item['track']
            print(idx, track['artists'][0]['name'], " – ", track['name'])

    def update_timebar_position(self):
        pos = self.current_song_timestamp/self.current_song_length
        if pos >= 0.99:
            self.update_current_info()
            return
        self.ids.time_bar.value = pos

    def update_current_info(self):
        playback_info = get_current_playback_state()
        if playback_info:
            if playback_info["is_playing"]:
                self.is_playing = True
                self.ids.stop_start_button.source = PAUSE_BUTTON_SRC
            else:
                self.is_playing = False
                self.ids.stop_start_button.source = PLAY_BUTTON_SRC

            self.current_song_timestamp = playback_info['progress_ms']
            self.current_song_length = playback_info['item']['duration_ms']
            self.update_timebar_position()

            self.track_image_source = playback_info['item']['album']['images'][0]['url']
            self.ids.track_image.source = self.track_image_source

            self.current_song_name = playback_info['item']['name']
            self.current_artist_name = playback_info['item']['artists'][0]['name']
            self.ids.song_name.text = self.current_song_name
            self.ids.artist_name.text = self.current_artist_name
        else:
            self.current_song_timestamp = self.current_song_length


    def play_pause(self, widget):
        playback_info = get_current_playback_state()
        if playback_info is not None:
            state = playback_info["is_playing"]
            if state:
                widget.source = PLAY_BUTTON_SRC
                sp.pause_playback()
                self.is_playing = False
            else:
                widget.source = PAUSE_BUTTON_SRC
                sp.start_playback()
                self.is_playing = True
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
            if self.is_playing:
                sp.pause_playback()
                self.is_playing = True
            new_position: int = int(widget.value * self.current_song_length)

            if playback_info['context'] is None:
                sp.start_playback(uris=[playback_info['item']['uri']], position_ms=new_position)
            else:
                sp.start_playback(context_uri=playback_info['context']['uri'], offset={"uri": playback_info['item']['uri']}, position_ms=new_position)
            self.current_song_timestamp = new_position

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


class MainApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MainApp().run()
