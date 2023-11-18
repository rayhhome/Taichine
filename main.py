from comparison import backend_process

import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.core.window import Window

from plyer import filechooser
import os
from os import system, getcwd, listdir, makedirs
from os.path import join, isfile, split

Window.minimum_width = 800
Window.minimum_height = 600
# Window.fullscreen = 'auto'

# global variable
tolerance = 5
preparation_time = 5

path_selected = None
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
  def set_value(self):
    preparation_time = self.ids.preparation_slider.value
    tolerance = self.ids.tolerance_slider.value
    print("Current Preparation Time:", preparation_time)
    print("Current Tolerance: ", tolerance)

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
      self.ids['reference_image'].source = join('.', 'poses', seq_id, pos_id + '.png')
    elif mode == 'custom':
      self.ids['reference_image'].source = join('.', 'user_poses', seq_id, pos_id + '.png')
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
      if (not os.path.exists(join('.', 'user_input'))):
        os.makedirs(join('.', 'user_input'))
      camera.export_to_png(join('.', 'user_input', 'user.png'))

      # Ray: backend processing moved to move_on() 
      # backend_process()
      self.move_on()

    self.start_countdown(finish_callback)

    # Start backend processing
    # DONE @ Ray: Need a parameter to know:
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

class TrimmedCamera(Camera):
  # https://stackoverflow.com/questions/67967041/how-can-i-use-kivy-to-zoom-in-or-zoom-out-live-camera
  region_x = NumericProperty(200)
  region_y = NumericProperty(0)
  region_w = NumericProperty(240)
  region_h = NumericProperty(480)
  
  def on_tex(self, camera):
    self.texture = texture = camera.texture
    # get some region
    self.texture = self.texture.get_region(self.region_x, self.region_y, self.region_w, self.region_h)
    self.texture_size = list(texture.size)
    self.canvas.ask_update()

class CustomScreen(Screen):

  def __init__(self, **kwargs):
    self.curr_dir = curr_dir = getcwd()
    self.poses_folder = join(curr_dir, "user_poses")
    print("self.curr_dir: ", self.curr_dir)
    self.cancel = False
    super().__init__(**kwargs)

  def select_file(self):
    system(f"mkdir {self.poses_folder}")
    filechooser.open_file(on_selection = self.selected, multiple=True)
    
  def selected(self, selection):
    # print("len(selection) = ", len(selection))
    if(len(selection) == 0):
      self.cancel = True 
      return
    # print("self.cancel", self.cancel)
    # print("selection = ", selection)
    globals()['path_selected'] = selection
    # print("globals()['path_selected']: ", globals()["path_selected"])
    
class PoseSequenceItem(Widget):

  # def exit_button(self, posesList):
  #   print("\n\nEXIT button:")
  #   print("posesList = ", posesList)

  # def left_button(self):
  #   print("\n\nLEFT button pressed!\n\n")

  # def right_button(self):
  #   print("\n\nRIGHT button pressed!\n\n")
  #   # for children in self.children:
  #   #     print(children)
  pass

class ConfirmScreen(Screen):

  def __init__(self, **kwargs):

    super(ConfirmScreen, self).__init__(**kwargs)
    self.filename=""
    self.curr_dir = getcwd()
    self.new_filename=""
    self.display_label=None
    self.posesList = []
    self.filenameList = []
    self.poseLabel = ""
    # self.textbox = None

  def on_pre_enter(self, *largs):
    print("self.curr_dir: ", self.curr_dir)
    # print("new screen globals()['path_selected']: ", globals()['path_selected'])
    #  height=30,

    self.posesList = globals()['path_selected']

    num_poses = len(self.posesList)

    for j in range(num_poses):
      splitList = self.posesList[j].split('\\')
      filename = splitList[-1]
      self.filenameList.append(filename)

    self.poseLabel = self.filenameList[0].split('.')[0]

    # print("self.filenameList = ", self.filenameList)
    def on_enter(instance): #, value
      print("value: ", instance.text)
      self.poseLabel = instance.text
      self.display_label.text = f'[color=121212]pose / pose sequence name: {instance.text}'

    # grid_layout = GridLayout(rows=1, orientation='lr-tb', padding=5, size_hint=(1, 0.7), pos_hint={'center_x': 0.5,'center_y': 0.55})
    # self.add_widget(grid_layout)
    
    # new children widgets are "added from the front"
    for i in range(num_poses):
      pose_item = PoseSequenceItem()
      pose_item.ids.pose_image.source = self.posesList[i]
      pose_item.ids.image_label.text = self.filenameList[i]
      self.ids.grid_layout.add_widget(pose_item)
    
    self.posesList.reverse()

    
    # for i2 in range(num_poses):
    #   print("child ", i2, " : ", self.ids.grid_layout.children[i2].ids.pose_image.source)
    #   print(f"self.posesList[{i2}] : ", self.posesList[i2])
    textLabel = Label(text='Enter Pose or Pose Sequence Name Here:', color=(0,0,0,1), pos_hint={'center_x': 0.5, 'center_y': 0.79})
    self.add_widget(textLabel)
    textbox = TextInput(size_hint=(0.3, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.75}, cursor_blink=True, multiline=False)
    textbox.bind(on_text_validate=on_enter)
    self.add_widget(textbox)

    # print("file_label: ", self.file_label)
    # print("path_selected: ", path_selected)
    self.display_label = Label(text=f'[color=121212]pose / pose sequence name: {self.poseLabel}', markup=True, size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.71}, background_color=(0,0,1,1))
    self.add_widget(self.display_label)

  def exit_button(self, img_src):
    # print("\n\nEXIT button:")
    # print("img_src = ", img_src)
    # print("self.posesList: ", self.posesList)
    # print("self.ids.grid_layout.children[0]: ", self.ids.grid_layout.children[0].ids.pose_image.source)
    # print("self.ids.grid_layout.children[1]: ", self.ids.grid_layout.children[1].ids.pose_image.source)

    num_poses = len(self.posesList)
    # print("num_poses", num_poses)
    # print("len(self.ids.grid_layout.children)", len(self.ids.grid_layout.children))
    
    for i in range(num_poses):
      if(self.posesList[i] == img_src):
        self.posesList.pop(i)
        self.ids.grid_layout.remove_widget(self.ids.grid_layout.children[i])
        break    

  def left_button(self, img_src):
    # print("\n\nLEFT button pressed!\n\n")
    # num_poses = len(self.posesList)
    # # print("num_poses", num_poses)
    # # print("len(self.ids.grid_layout.children)", len(self.ids.grid_layout.children))
    num_poses = len(self.posesList)

    for i in range(num_poses):
      if(self.posesList[i] == img_src):
        img_index = i
        break
    if(img_index == (num_poses - 1)):
      return
    else:
      swap(self.posesList, i, i + 1)
      swap(self.ids.grid_layout.children, img_index, img_index + 1)

  def right_button(self, img_src):
    # print("\n\nRIGHT button pressed!\n\n")
    num_poses = len(self.posesList)

    for i in range(num_poses):
      if(self.posesList[i] == img_src):
        img_index = i
        break
    if(img_index == 0):
      return
    else:
      swap(self.posesList, i - 1, i)
      swap(self.ids.grid_layout.children, img_index - 1, img_index)
  
  def confirmed(self):
    src = globals()['path_selected']
    # print("src: ", src)
    dest = []
    # print("self.curr_dir: ", self.curr_dir)
    
    # for i in range(len(src)):
    
    system(f"mkdir {self.curr_dir}\\user_poses\\{self.poseLabel}")


    for i in range(len(src)):

      filename, filetype = getFileTypeAndName(src[i]) 
    
      if(self.new_filename != ""):
        filename = self.new_filename

      # print("   src_path  : ", src_path
      dest.append(f"{self.curr_dir}\\user_poses\\{self.poseLabel}\\{filename}.{filetype}")
      
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

def swap(list, indexA, indexB):
  temp = list[indexA]
  list[indexA] = list[indexB]
  list[indexB] = temp

def getFileTypeAndName(fileSrc):
  print("fileSrc", fileSrc)
  src_split_list = fileSrc.split('\\')
  print("src_split_list", src_split_list)
  filenameAndType = src_split_list[-1]
  filename_list = filenameAndType.split('.')
  print("filename_list", filename_list)
  print(filename_list)
  filetype = filename_list[-1]
  filename = filename_list[0]

  return filename, filetype

class TaichineApp(App):
  pass 

if __name__ == '__main__':
  TaichineApp().run()