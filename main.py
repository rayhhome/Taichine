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
from kivy.graphics import Color, Line, Rectangle, Ellipse

from plyer import filechooser
import os
from os import system, getcwd, listdir, makedirs
from os.path import join, isfile, split

import numpy as np

import json

tolerance = 5
preparation_time = 5

Window.minimum_width = 800
Window.minimum_height = 600
# Window.fullscreen = 'auto'

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
  def set_reference_image(self, mode, seq_id, pos_id):   
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

  # Ray: set the value for the countdown timer
  def set_countdown(self, seconds):
    self.countdown = seconds

  # Ray: actually start the countdown timer 
  #      and call the callback function when countdown reaches 0
  def start_countdown(self, callback_func):
    Animation.cancel_all(self)
    self.anim = Animation(countdown=0, duration=self.countdown)
    self.anim.bind(on_complete=callback_func)
    self.anim.start(self)

  def draw_reference_skeleton(self, pose_coords):
    # Deal with input coordinates
    all_x = pose_coords[:,0]
    all_y = pose_coords[:,1]
    min_x = np.min(all_x)
    max_x = np.max(all_x)
    min_y = np.min(all_y)
    max_y = np.max(all_y)
    input_width = max_x - min_x
    input_height = max_y - min_y

    # Calculate offsets and scales to fit the canvas
    x_offset = 0
    y_offset = 0
    x_scale = 1
    y_scale = 1

    draw_width = self.ids.skeleton_canvas.width * 0.8
    draw_height = self.ids.skeleton_canvas.height * 0.8
    input_dimension = input_width / input_height
    canvas_dimension = draw_width / draw_height

    if input_dimension > canvas_dimension:
      # Input is wider than canvas
      x_scale = draw_width / input_width
      y_scale = x_scale
      y_offset = (draw_height - input_height * y_scale) / 2 + draw_height * 0.1
      x_offset = draw_width * 0.1
    else:
      # Input is taller than canvas
      y_scale = draw_height / input_height
      x_scale = y_scale
      x_offset = (draw_width - input_width * x_scale) / 2 + draw_width * 0.1
      y_offset = draw_height * 0.1

    # Modify coordinates to fit the canvas
    all_x = (all_x - min_x) * x_scale + x_offset
    all_y = (max_y - all_y) * y_scale + y_offset

    # Start drawing
    with self.ids.skeleton_canvas.canvas:
      # Draw the reference pose
      Color(0, 0, 1, 1) # Reference in Blue

      # Go through all limbs
      line_width = 4
      head_radius = 40
      # Torso -> Right Arm Top
      Line(points=[all_x[1], all_y[1], all_x[2], all_y[2]], width=line_width)
      # Right Arm Top -> Right Arm Middle
      Line(points=[all_x[2], all_y[2], all_x[3], all_y[3]], width=line_width)
      # Right Arm Middle -> Right Hand
      Line(points=[all_x[3], all_y[3], all_x[4], all_y[4]], width=line_width)
      # Torso -> Left Arm Top
      Line(points=[all_x[1], all_y[1], all_x[5], all_y[5]], width=line_width)
      # Left Arm Top -> Left Arm Middle
      Line(points=[all_x[5], all_y[5], all_x[6], all_y[6]], width=line_width)
      # Left Arm Middle -> Left Hand
      Line(points=[all_x[6], all_y[6], all_x[7], all_y[7]], width=line_width)
      # Torso -> Waist
      Line(points=[all_x[1], all_y[1], all_x[8], all_y[8]], width=line_width)
      # Waist -> Right Leg Top
      Line(points=[all_x[8], all_y[8], all_x[9], all_y[9]], width=line_width)
      # Right Leg Top -> Right Leg Middle
      Line(points=[all_x[9], all_y[9], all_x[10], all_y[10]], width=line_width)
      # Right Leg Middle -> Right Foot
      Line(points=[all_x[10], all_y[10], all_x[11], all_y[11]], width=line_width)
      # Waist -> Left Leg Top
      Line(points=[all_x[8], all_y[8], all_x[12], all_y[12]], width=line_width)
      # Left Leg Top -> Left Leg Middle
      Line(points=[all_x[12], all_y[12], all_x[13], all_y[13]], width=line_width)
      # Left Leg Middle -> Left Foot
      Line(points=[all_x[13], all_y[13], all_x[14], all_y[14]], width=line_width)
      # Left Foot -> Left Toe
      Line(points=[all_x[14], all_y[14], all_x[19], all_y[19]], width=line_width)
      # Right Foot -> Right Toe
      Line(points=[all_x[11], all_y[11], all_x[22], all_y[22]], width=line_width)
      # Head -> Torso
      Line(points=[all_x[0], all_y[0], all_x[1], all_y[1]], width=line_width)
      Ellipse(pos=(all_x[0] - head_radius, all_y[0] - head_radius), size=(head_radius * 2, head_radius * 2))

  def draw_user_skeleton(self, pose_coords, pose_angles, checklist):
    # Start drawing
    with self.ids.skeleton_canvas.canvas:
      # Draw the user pose
      Color(0, 1, 0, 1) # Correct in Green
      Color(1, 0, 0, 1) # Wrong in Red
    pass

  def move_on(self):
    print("move_on() called")
    
    # joint_data = backend_process(self.mode, self.current_seq, self.current_pose)
    
    # if joint_data == None:
    #   print("joint_data is None")

    # # Drawing pipeline
    # # Extract all joint data
    # pose_pass = joint_data[0]
    # reference_pose_coords = joint_data[1]
    # user_pose_coords = joint_data[2]
    # limb_checklist = joint_data[3]
    # reference_pose_angles = joint_data[4]
    # user_pose_angles = joint_data[5]

    canvas_to_draw = self.ids.skeleton_canvas
    canvas_to_draw.canvas.clear()  

    # Show Signal
    with canvas_to_draw.canvas:
    #   if pose_pass:
    #     Color(0, 1, 0, 1) # Correct in Green
    #   else:
    #     Color(1, 0, 0, 1) # Wrong in Red
    #   Rectangle(pos=(0, 0), size=(canvas_to_draw.width, canvas_to_draw.height))
      Color(0, 0, 0, 1) # Background in Black
      Rectangle(pos=(10, 10), size=(canvas_to_draw.width - 20, canvas_to_draw.height - 20))

    with open("SampleOutput\\1\\1_keypoints.json", 'r') as file:
      local_data = json.load(file)
    reference_pose_coords = local_data["people"][0]["pose_keypoints_2d"]
    reference_pose_coords = np.array(reference_pose_coords).reshape(-1, 3)
    reference_pose_coords = reference_pose_coords[:, :2]

    # Draw poses  
    self.draw_reference_skeleton(reference_pose_coords)
    # self.draw_user_skeleton(user_pose_coords, user_pose_angles, limb_checklist)

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
    filechooser.open_file(on_selection = self.selected)
    
  def selected(self, selection):
    # print("len(selection) = ", len(selection))
    if(len(selection) == 0):
      self.cancel = True 
      return
    print("self.cancel", self.cancel)
    globals()['path_selected'] = selection[0]
    print("globals()['path_selected']: ", globals()["path_selected"])
    
class PoseSequenceItem(Widget):
  def exit_button(self):
    print("\n\nEXIT button pressed!\n\n")

  def left_button(self):
    print("\n\nLEFT button pressed!\n\n")

  def right_button(self):
    print("\n\nRIGHT button pressed!\n\n")
    # for children in self.children:
    #     print(children)
  pass

class ConfirmScreen(Screen):

  def __init__(self, **kwargs):

    super(ConfirmScreen, self).__init__(**kwargs)
    self.filename=""
    self.curr_dir = getcwd()
    self.new_filename=""
    self.display_label=None
    self.posesList = []
    # self.textbox = None

  def on_pre_enter(self, *largs):
    print("self.curr_dir: ", self.curr_dir)
    # print("new screen globals()['path_selected']: ", globals()['path_selected'])
    #  height=30,

    path_selected = globals()['path_selected']
    print("path_selected: ", path_selected)
    pathIsFolder = os.path.isdir(path_selected)
    
    if(pathIsFolder):
      
      # code from https://www.geeksforgeeks.org/how-to-iterate-over-files-in-directory-using-python/ 

      for file in os.listdir(path_selected):
        file_path = os.path.join(path_selected, file)
        if(os.path.isfile(file_path)):
          self.posesList.append(file_path)
    else:
      self.posesList.append(path_selected)

    num_poses = len(self.posesList)
    src_split_list = path_selected.split('\\')
    self.file_label = src_split_list[-1]

    def on_enter(instance): #, value
      # print("value: ", instance.text)
      self.new_filename = instance.text
      filename, file_type = getFileTypeAndName(self.file_label)
      # self.display_label.text = f'[color=121212]{self.new_filename}.{file_type}'

    # grid_layout = GridLayout(rows=1, orientation='lr-tb', padding=5, size_hint=(1, 0.7), pos_hint={'center_x': 0.5,'center_y': 0.55})
    # self.add_widget(grid_layout)

    for i in range(num_poses):
      pose_item = PoseSequenceItem()
      pose_item.ids.pose_image.source = self.posesList[i]
      self.ids.grid_layout.add_widget(pose_item)
      # grid_layout.add_widget(pose_item)
    
    # print("self.ids.grid_layout.children[0].pose_image.pos = ", self.ids.grid_layout.children[0].ids.pose_image.pos)
    # print("self.ids.grid_layout.children[0].pose_image.size = ", self.ids.grid_layout.children[0].ids.pose_image.size)
    # print("\nself.ids.grid_layout.children[0].ids.rel_layout.pos = ", self.ids.grid_layout.children[0].ids.rel_layout.pos)
    # print("self.ids.grid_layout.children[0].ids.rel_layout.size = ", self.ids.grid_layout.children[0].ids.rel_layout.size)
    
    pose_item2 = PoseSequenceItem()
    pose_item2.ids.pose_image.source = 'C:\\Users\\jerry\\user_poses\\mole.png'
    self.ids.grid_layout.add_widget(pose_item2)
    # print("\n\nself.ids.grid_layout.children", self.ids.grid_layout.children)
    # print("self.ids.grid_layout.children[0].ids.pose_image.children", self.ids.grid_layout.children[0].ids.pose_image.children)
    # grid_layout.add_widget(pose_item2)
    # print("self.ids.grid_layout.children[1].pose_image.pos = ", self.ids.grid_layout.children[1].ids.pose_image.pos)
    # print("self.ids.grid_layout.children[1].pose_image.children = ", self.ids.grid_layout.children[1].ids.pose_image.children)
    # print("self.ids.grid_layout.children[1].ids.rel_layout.pos = ", self.ids.grid_layout.children[1].ids.rel_layout.pos)
    
    # print("\nself.ids.grid_layout.children[1].ids.rel_layout.size = ", self.ids.grid_layout.children[1].ids.rel_layout.size)
    # print("self.ids.grid_layout.children[1].ids.rel_layout.canvas.get_group('a')[0].size = ", self.ids.grid_layout.children[1].ids.rel_layout.canvas.get_group('a')[0].size)
    
    # print("\nself.ids.grid_layout.children[1].ids.rel_layout.pos = ", self.ids.grid_layout.children[1].ids.rel_layout.pos)
    # print("self.ids.grid_layout.children[1].ids.rel_layout.canvas.get_group('a')[0].pos = ", self.ids.grid_layout.children[1].ids.rel_layout.canvas.get_group('a')[0].pos)
    # print("self.ids.grid_layout.children[0].ids.pose_image.source = ", self.ids.grid_layout.children[0].ids.pose_image.source)
    # print("self.ids.grid_layout.children[1].ids.pose_image.source = ", self.ids.grid_layout.children[1].ids.pose_image.source)
    textbox = TextInput(size_hint=(0.3, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.8}, cursor_blink=True, multiline=False)
    textbox.bind(on_text_validate=on_enter)
    self.add_widget(textbox)
    
    
    # print("filename: ", filename)

    # print("file_label: ", self.file_label)
    # print("path_selected: ", path_selected)
    # self.display_label = Label(text=f'[color=121212]{self.file_label}', markup=True, size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.6}, background_color=(0,0,1,1))
    # # self.display_label.bind(text=on_enter)
  
    # self.display_image = Image(source=path_selected, size_hint=(0.3, 0.3), pos_hint={'center_x': 0.5, 'center_y': 0.4})
    
    # self.add_widget(self.display_image)
    # self.add_widget(self.display_label)

  
  
  def confirmed(self):
    src = globals()['path_selected']
    # print("src: ", src)
    dest = []
    # print("self.curr_dir: ", self.curr_dir)
    
    # for i in range(len(src)):
      
    # removing old filename from path
    filename, filetype = getFileTypeAndName(src[0]) # = src_split_list.pop(-1)
    pose_seq_dir = filename
    # join_char = "\\"
    # src_path = join_char.join(src_split_list)
    
    if(self.new_filename != ""):
      filename = self.new_filename

    # print("   src_path  : ", src_path)
    system(f"mkdir {self.curr_dir}\\user_poses\\{filename}")
    if(len(self.posesList) == 1):
      dest.append(f"{self.curr_dir}\\user_poses\\{filename}\\{filename}.{filetype}")
    else:
      dest.append(f"{self.curr_dir}\\user_poses\\{pose_seq_dir}")
      
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