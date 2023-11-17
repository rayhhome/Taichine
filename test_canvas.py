import kivy
kivy.require('2.2.1')

from kivy.uix.screenmanager import Screen

from kivy.app import App

class CanvasScreen(Screen):
    pass

class TestDrawApp(App):
    pass

if __name__ == '__main__':
    TestDrawApp().run()