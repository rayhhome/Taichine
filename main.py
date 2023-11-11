import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from time import strftime

from plyer import filechooser
from os import system, getcwd, listdir, chdir
from os.path import join, isfile, split

Window.minimum_width = 800
Window.minimum_height = 600

# pose item
class PoseItem(ButtonBehavior, BoxLayout):
  id = StringProperty('')
  image = StringProperty('')
  label = StringProperty('')
  mode = StringProperty('')
  pass

# menu screen
class MenuScreen(Screen):
  pass

# mode screen, choose between integrated/custom poses
class ModeScreen(Screen):
  pass

# selection screen
class SelectionScreen(Screen):
  mode = StringProperty('')

  def set_all(self):
    if self.mode == 'integrated':
      pose_dir = 'poses'
    elif self.mode == 'custom':
      pose_dir = 'user_poses'
    menu = self.ids['menu_grid']
    menu.bind(minimum_height = menu.setter('height'))
    allseqs = listdir(join('.', pose_dir))
    allseqs.sort()

    menu.clear_widgets()
    for seq in allseqs:
      if isfile(join('.', pose_dir, seq, '1.png')):
        pose = PoseItem()
        pose.id = seq
        pose.image = join('.', pose_dir, seq, '1.png')
        pose.label = seq
        pose.mode = self.mode
        print(pose)
        menu.add_widget(pose)  
      else:
        print('not a file')
  pass

# setting screen
class SettingScreen(Screen):
  pass

# training screen
class TrainingScreen(Screen):
  countdown = NumericProperty(10) 

  def set_reference_image(self, mode, seq_id, pos_id):
    if mode == 'integrated':
      self.ids['reference_image'].source = join('.', 'poses', seq_id, pos_id+'.png')
    elif mode == 'custom':
      self.ids['reference_image'].source = join('.', 'user_poses', seq_id, pos_id+'.png')
    self.ids['reference_image'].reload()

  def capture(self):
    '''
    https://stackoverflow.com/questions/41937173/kivy-simple-countdown-minute-and-second-timer
    '''
    Animation.cancel_all(self)
    self.anim = Animation(countdown=0, duration=self.countdown)

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
    self.poses_folder = join(curr_dir, "user_poses")
    print("self.curr_dir: ", self.curr_dir)
    super().__init__(**kwargs)

  def select_file(self):
    system(f"mkdir -p {self.poses_folder}")
    filechooser.open_file(on_selection = self.selected)
    
    # path = filechooser.open_file(title="Choose an Image to Upload!", 
    #                      filters=[("PNG Files", "*.png")])
    
  def selected(self, selection):
    src = selection
    dest = []
    print("self.curr_dir: ", self.curr_dir)
    
    for i in range(len(selection)):
      src_split_list = split(src[i])
      filename = src_split_list[1] 
      dest.append(join(self.curr_dir, "user_poses", filename))

  
    for j in range(len(dest)):
        cmd = f'copy "{src[j]}" "{dest[j]}"'
        print("src: ", src[j])
        print("dest: ", dest[j])
        system(cmd)
    # print(selection[0])

    chdir(self.curr_dir)
        
    print("done")

class TaichineApp(App):
  pass 

if __name__ == '__main__':
  TaichineApp().run()