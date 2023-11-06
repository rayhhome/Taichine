from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.core.window import Window
from time import strftime

# training screen
class TrainingScreen(Screen):
  a = NumericProperty(10) 

  def capture(self):
    Animation.cancel_all(self)
    self.anim = Animation(a=0, duration=self.a)

    def finish_callback(animation, incr_crude_clock):
      '''
      https://kivy.org/doc/stable/examples/gen__camera__main__py.html
      '''
      capture_button = self.ids['capture']      
      capture_button.text = "Capture"
      camera = self.ids['camera']
      timestr = strftime("%Y%m%d_%H%M%S")
      camera.export_to_png("IMG_{}.png".format(timestr))
      print("Captured") 

    self.anim.bind(on_complete=finish_callback)
    self.anim.start(self) 

  def on_a(self, instance, value):
    capture_button = self.ids['capture']
    capture_button.text = str(round(value, 1))

class TrainingApp(App):
  def build(self):
    Window.minimum_width, Window.minimum_height = (800, 600)    
    smanager = ScreenManager()
    smanager.add_widget(TrainingScreen())    
    return smanager
  
if __name__ == '__main__':
  TrainingApp().run()
