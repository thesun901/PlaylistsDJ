import spotipy
import kivy
from kivy.app import App
from kivy.uix.widget import Widget


class MainLayout(Widget):
    pass

class TestingApp(App):
    def build(self):
        return MainLayout()


if __name__ == '__main__':
    TestingApp.run()
