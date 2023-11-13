from comparison import backend_process

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

from PIL import Image

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
  mode = StringProperty('')
  current_seq  = StringProperty('')
  current_pose = StringProperty('')

  def set_reference_image(self, mode, seq_id, pos_id):
    # Ray: there are two modes: integrated and custom
    #      integrated: use the default poses
    #      custom: use the user uploaded poses
    #      seq_id: the sequence id of the pose, i.e. the folder name
    #      pos_id: the pose id of the pose, i.e. the image name
    #        note that the image name should always be 1, 2, 3, 4, 5...
    #        because the order of the images matters

    #        this means if we want to allow for custom pose sequenes,
    #        we need rename the images in the folder to these numbers
    #        according to their order      

    if mode == 'integrated':
      self.ids['reference_image'].source = join('.', 'poses', seq_id, pos_id+'.png')
    elif mode == 'custom':
      self.ids['reference_image'].source = join('.', 'user_poses', seq_id, pos_id+'.png')
    self.ids['reference_image'].reload()
    self.current_seq  = seq_id
    self.current_pose = pos_id

  def start_training(self):
    '''
    https://stackoverflow.com/questions/41937173/kivy-simple-countdown-minute-and-second-timer
    '''

    def finish_callback(animation, training_screen):
      '''
      https://kivy.org/doc/stable/examples/gen__camera__main__py.html
      '''
      start_button = self.ids['start_button']
      start_button.text = "Start"
      camera = self.ids['camera']
      camera.export_to_png("user.png")
      camera.export_to_png(".\\user_input\\user.png")

      # Ray: backend processing moved to move_on() 
      # backend_process()
      self.move_on()

    self.start_countdown(finish_callback);

    # Start backend processing
    # TODO @ Ray: Need a parameter to know:
    # 1. Whether it is user pose or default pose
    #   Ray: to access the pose mode, use self.mode, which can be either "integrated" or "custom"
    # 2. The pose name to find the coordinates
    #   Ray: to access the pose name, use:
    #     a. self.current_seq , which can be "01 - Commence form", "02 - Open and close", "03 - Single whip"...
    #     b. self.current_pose, which can be "1.png", "2.png", "3.png"...

  def set_countdown(self, seconds):
    # Ray: set the value for the countdown timer
    self.countdown = seconds

  def start_countdown(self, callback_func):
    # Ray: actually start the countdown timer 
    #      and call the callback function when countdown reaches 0
    Animation.cancel_all(self)
    self.anim = Animation(countdown=0, duration=self.countdown)
    self.anim.bind(on_complete=callback_func)
    self.anim.start(self)

  def move_on(self):
    print("move_on() called")
    backend_process()
    # Ray (Thoughts on the flow): 
    # Check back_process return
    # If some body part outside of frame:
    #   Display flashing warning
    #   Verbal warning played
    # Else if some body part is wrong:
    #   Display skelectons with wrong body part
    #   Verbal instruction played
    # Else:
    # -- IF MVP --
    #   Display congratulations (Probably need a result screen, TBD)
    # -- IF FULL (WITH POSE SEQUENCE) --
    #   If last pose:
    #     Display congratulations (Probably need a result screen, TBD)
    #   Else:
    #     Switch reference image to next pose using set_reference_image()
    #     Display new reference and user skelectons with correct body part
    #     Verbal instruction reading "great job" and the next pose name
    # Set up countdown timer here, probably shorter than 10 seconds 
    #   (5 seconds? Use set_countdown() to set the time)
    # Start countdown and set call_back to move_on() again

  def on_countdown(self, instance, value):
    # Ray: this is for animation of the start button text
    #      it starts with "on" for a purpose: to match weired kivy syntax
    #      don't call it in any function in this class
    #      don't call it in any function in this class
    #      don't call it in any function in this class
    start_button = self.ids['start_button']
    start_button.text = str(round(value, 1))

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
      dest.append(join(self.curr_dir, "user_poses", "custom", "1.png"))

    for j in range(len(dest)):
      cur_img = Image.open(r'{}'.format([src[j]]))
      cur_img.save(r'{}'.format([dest[j]]))
    # print(selection[0])



    chdir(self.curr_dir)

class TaichineApp(App):
  pass 

if __name__ == '__main__':
  TaichineApp().run()