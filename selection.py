from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.core.window import Window

from plyer import filechooser
from os import system, getcwd
from os import listdir
from os.path import join, isfile

taichi_name = [
  "Commence form",
  "Parting wild horse's mane (3 times)",
  "White crane spreads its wings",
  "Brush knee and press (3 times)",
  "Play the lute",
  "Repulse the monkey (4 times)",
  "Grasp the sparrow's tail (left and right)",
  "Single whip",
  "Wave hands like clouds",
  "Single whip",
  "High pat on horse",
  "Right heel kick",
  "Strike opponent's ears with fists",
  "Turn around, left heel kick",
  "Snake creeps down",
  "Golden rooster standing on left leg",
  "Snake creeps down",
  "Golden rooster standing on right leg",
  "Fair lady works the shuttles (right and left)",
  "Needles at sea bottom",
  "Fan through back",
  "Turn around, block, parry and punch",
  "Withdraw and push",
  "Cross hands and close form"
]

# pose item
class PoseItem(BoxLayout, ButtonBehavior):
  id = StringProperty('')
  image = StringProperty('')
  label = StringProperty('')
  pass

# selection screen
class SelectionScreen(Screen):
    def __init__(self, **kw):
      super().__init__(**kw)
      menu = self.ids['menu_grid']
      menu.bind(minimum_height=menu.setter('height'))
      allseqs = listdir('./poses')
      allseqs.sort()

      for seq in allseqs:
        if isfile(join('./poses', seq, '1.png')):
          pose = PoseItem()
          pose.id = seq
          pose.image = './poses/' + seq + '/1.png'
          pose.label = seq + ' - ' + taichi_name[int(seq) - 1]
          print(pose)
          menu.add_widget(pose)  
        else:
          print('not a file')
    pass

class SelectionApp(App):
  def build(self):
    Window.minimum_width, Window.minimum_height = (800, 600)    
    smanager = ScreenManager()
    smanager.add_widget(SelectionScreen())
    return smanager
  
if __name__ == '__main__':
  SelectionApp().run()
