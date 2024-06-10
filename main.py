import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"
from spotify_setup import sp
from kivy.app import App
from kivy.uix.behaviors.drag import DragBehavior
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
import math
from kivy.uix.label import Label
import processing_functions

PLAY_BUTTON_SRC = "pictures/play_button.png"
PAUSE_BUTTON_SRC = "pictures/pasue_button.png"


class DragCircle(DragBehavior, Button):
    def good_distance(self, x, y, rx, ry):
        print(math.sqrt(x**2 + y**2), rx, x, y)
        return math.sqrt(x**2 + y**2) < rx*2

class MainLayout(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def btn(self):
        results = sp.current_user_saved_tracks()
        print(results)
        for idx, item in enumerate(results['items']):
            track = item['track']
            print(idx, track['artists'][0]['name'], " – ", track['name'])

    def play_pause(self, widget):
        if sp.current_playback()['is_playing']:
            widget.source = PAUSE_BUTTON_SRC
            sp.pause_playback()
        else:
            widget.source = PLAY_BUTTON_SRC
            sp.start_playback()

    def stop(self):
        sp.pause_playback()

    def start(self):
        if not sp.current_playback()['is_playing']:
            sp.start_playback()
            print(sp.audio_features(sp.current_playback()['item']['id']))
          #  print(sp.audio_analysis(sp.current_playback()['item']['id']))

    def animate(self, widget, *args):
        first_size = tuple(widget.size_hint)
        og_color = tuple(widget.background_color)
        anim = Animation(
            size_hint=(1, 1),
            background_color=(0, 0, 1, 1),
            duration=1
        )
        anim += Animation(
            size_hint=first_size,
            background_color=og_color

        )
        anim.start(widget)




class TestingApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    TestingApp().run()
