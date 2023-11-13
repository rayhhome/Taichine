from comparison import backend_process

import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from time import strftime

from plyer import filechooser
import os
from os import system, getcwd, listdir, chdir
from os.path import join, isfile, split

Window.minimum_width = 800
Window.minimum_height = 600

confirm_selection = None
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
    backend_process(self.mode, self.current_seq, self.current_pose)
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
    globals()['confirm_selection'] = src
    print("globals()['confirm_selection']: ", globals()["confirm_selection"])
    # dest = []
    # print("self.curr_dir: ", self.curr_dir)
    
    # for i in range(len(selection)):
    #     src_split_list = src[i].split('\\')
    #     filename = src_split_list[-1] 
    #     dest.append(f"{self.curr_dir}\\user_poses\\{filename}")
    
    # print("src: ", src)
    # for j in range(len(dest)):
    #   if os.name == 'nt':  # Windows
    #     cmd = f'copy "{src[j]}" "{dest[j]}"'
    #   else:  # Unix/Linux
    #     cmd.replace("\\", "/")
    #     cmd = f'cp "{src}" "{dst}"'
        
    #   print("src: ", src[j])
    #   print("dest: ", dest[j])
    #   system(cmd)
    # # print(selection[0])
  
    # print("done")

    # chdir(self.curr_dir)

def getFileTypeAndName(fileSrc):
  print("fileSrc", fileSrc)
  src_split_list = fileSrc.split('\\')
  print("src_split_list", src_split_list)
  filenameAndType = src_split_list[-1]
  filename_list = filenameAndType.split('.')
  print(filename_list)
  filetype = filename_list[-1]
  filename = filename_list[0]

  return filename, filetype

class ConfirmScreen(Screen):

  def __init__(self, **kwargs):

    super(ConfirmScreen, self).__init__(**kwargs)
    self.filename=""
    self.curr_dir = curr_dir = getcwd()
    self.new_filename=""
    self.display_label=None
    # self.textbox = None

  def on_pre_enter(self, *largs):
    print("self.curr_dir: ", self.curr_dir)
    # print("new screen globals()['confirm_selection']: ", globals()['confirm_selection'])
    #  height=30,

    confirm_selection = globals()['confirm_selection'][0]
    src_split_list = confirm_selection.split('\\')
    self.file_label = src_split_list[-1]

    def on_enter(instance): #, value
      # print("value: ", instance.text)
      self.new_filename = instance.text
      filename, file_type = getFileTypeAndName(self.file_label)
      self.display_label.text = f'[color=121212]{self.new_filename}.{file_type}'

    textbox = TextInput(size_hint=(0.3, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.7}, cursor_blink=True, multiline=False)
    textbox.bind(on_text_validate=on_enter)
    self.add_widget(textbox)
    
    
    # print("filename: ", filename)

    print("file_label: ", self.file_label)
    print("confirm_selection: ", confirm_selection)
    self.display_label = Label(text=f'[color=121212]{self.file_label}', markup=True, size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.6}, background_color=(0,0,1,1))
    # self.display_label.bind(text=on_enter)
  
    self.display_image = Image(source=confirm_selection, size_hint=(0.3, 0.3), pos_hint={'center_x': 0.5, 'center_y': 0.4})
    
    self.add_widget(self.display_image)
    self.add_widget(self.display_label)

  def confirmed(self):
    src = globals()['confirm_selection']
    # print("src: ", src)
    dest = []
    # print("self.curr_dir: ", self.curr_dir)
    
    # for i in range(len(src)):
      
    # removing old filename from path
    filename, filetype = getFileTypeAndName(src[0]) # = src_split_list.pop(-1)
    # join_char = "\\"
    # src_path = join_char.join(src_split_list)
    
    if(self.new_filename != ""):
      filename = self.new_filename

    # print("   src_path  : ", src_path)
    system(f"mkdir {self.curr_dir}\\user_poses\\{filename}")
    dest.append(f"{self.curr_dir}\\user_poses\\{filename}\\{filename}.{filetype}")
      
    # print("src: ", src)
    for j in range(len(dest)):
      if os.name == 'nt':  # Windows
        cmd = f'copy "{src[j]}" "{dest[j]}"'
      else:  # Unix/Linux
        cmd.replace("\\", "/")
        cmd = f'cp "{src}" "{dst}"'
      print("cmd: ", repr(cmd))
      system(cmd)
      print("src: ", src[j])
      print("dest: ", dest[j])
    # print(selection[0])

    print("done")

    # self.on_enter = on_enter()


class TaichineApp(App):
  pass 

if __name__ == '__main__':
  TaichineApp().run()