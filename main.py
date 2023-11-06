import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.core.window import Window

from time import strftime

from plyer import filechooser
from os import system, getcwd
from os import listdir
from os.path import join, isfile

# pose item
# class PoseItem(ButtonBehavior, Image):
#   id = StringProperty('')
#   image = StringProperty('')
#   label = StringProperty('')
#   pass

# menu screen
class MenuScreen(Screen):
  pass

# selection screen
class SelectionScreen(Screen):
    # allseqs = listdir('./poses')
    # for seq in allseqs:
    #   if isfile(join('./poses', seq)):
    #     pose = PoseItem()
    #     pose.id = seq
    #     pose.image = './poses/' + seq + '/0.jpg'
    #     pose.label = seq
    #     smanager.add_widget(pose)  
    pass

# setting screen
class SettingScreen(Screen):
  pass

# training screen
class TrainingScreen(Screen):
  a = NumericProperty(10) 

  def capture(self):
    '''
    https://stackoverflow.com/questions/41937173/kivy-simple-countdown-minute-and-second-timer
    '''
    Animation.cancel_all(self)
    self.anim = Animation(a=0, duration=self.a)

    def finish_callback(animation, training_screen):
      '''
      https://kivy.org/doc/stable/examples/gen__camera__main__py.html
      '''
      capture_button = self.ids['capture']      
      capture_button.text = "Capture"
      camera = self.ids['camera']
      timestr = strftime("%Y%m%d_%H%M%S")
      camera.export_to_png("IMG_{}.png".format(timestr))

    self.anim.bind(on_complete=finish_callback)
    self.anim.start(self) 

  def on_a(self, instance, value):
    capture_button = self.ids['capture']
    capture_button.text = str(round(value, 1))

class CustomScreen(Screen):

    def __init__(self, **kwargs):
        self.curr_dir = curr_dir = getcwd()
        self.poses_folder = f"{curr_dir}\\user_poses"
        print("self.curr_dir: ", self.curr_dir)
        super().__init__(**kwargs)

    def select_file(self):
        system(f"mkdir {self.poses_folder}")
        filechooser.open_file(on_selection = self.selected)
        
        # path = filechooser.open_file(title="Choose an Image to Upload!", 
        #                      filters=[("PNG Files", "*.png")])
    
    def selected(self, selection):
        src = selection
        dest = []
        print("self.curr_dir: ", self.curr_dir)
        
        for i in range(len(selection)):
            src_split_list = src[i].split('\\')
            filename = src_split_list[-1] 
            dest.append(f"{self.curr_dir}\\user_poses\\{filename}")

        
        for j in range(len(dest)):
            cmd = f'copy "{src[j]}" "{dest[j]}"'
            print("src: ", src[j])
            print("dest: ", dest[j])
            system(cmd)
        # print(selection[0])
    
        print("done")

class TaichineApp(App):
  def build(self):
    Window.minimum_width, Window.minimum_height = (800, 600)    
    smanager = ScreenManager()
    smanager.add_widget(MenuScreen())
    smanager.add_widget(SelectionScreen())
    smanager.add_widget(SettingScreen())
    smanager.add_widget(TrainingScreen())
    smanager.add_widget(CustomScreen())
    return smanager
    
if __name__ == '__main__':
  TaichineApp().run()