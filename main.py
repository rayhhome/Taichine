from comparison import backend_process

import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
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
from os import system, getcwd, listdir, remove
from os.path import join, isfile, exists
from math import ceil
from random import choice
from OpenPoseInter import parseImageFromPath

import numpy as np

import json

Window.minimum_width = 800
Window.minimum_height = 600
Window.fullscreen = 'auto'

# global variables
tolerance = 5
preparation_time = 15
move_on_time = 5

path_selected = None

tips = [
  'Tweak the tolerance slider in the setting screen to adjust the difficulty according to your condition.',
  'Tweak the preparation time slider in the setting screen to adjust the preparation time when the training starts.',
  'Tweak the move-on time slider in the setting screen to adjust the time interval between each pose.',
  'Make sure all your body parts are in the camera view to get optimal evaluation results.',
  'Upload your own pose sequences in the custom screen to train with your own poses.',
  'High score is not the goal. Please train with your own pace.',
  'Tai Chi is a long-term training. Please keep training and you will see the improvement.',
  'Please consult your doctor before training if you have any health concerns.',
  'Tai Chi is mostly for adjusting your breathing pace and enhancing cardiorespiratory endurance.',
  'Balance is the goal. Try to keep your balance as you train.',
  'Breath in when you move your arms up, breath out when you move your arms down.'
]

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
    sel_curr_dir = getcwd()
    print("sel_curr_dir: ", sel_curr_dir)
    if self.mode == 'integrated':
      pose_dir = 'poses'
    elif self.mode == 'custom':
      curr_dir = getcwd()
      print("curr_dir: ", curr_dir)
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
        print('not a file, file name should be :', join('.', pose_dir, seq, '1.png'))

# pose item (used in selection screen)
class PoseItem(ButtonBehavior, BoxLayout):
  id = StringProperty('')
  image = StringProperty('')
  label = StringProperty('')
  mode = StringProperty('')
  pass

# setting screen 
class SettingScreen(Screen):

  def set_value(self):
    global preparation_time
    global move_on_time
    global tolerance
    preparation_time = self.ids.preparation_slider.value
    move_on_time = self.ids.move_on_slider.value
    tolerance = self.ids.tolerance_slider.value
    print("Current Preparation Time:", preparation_time)
    print("Current Move On Time: ", move_on_time)
    print("Current Tolerance: ", tolerance)

# training screen
class TrainingScreen(Screen):
  countdown = NumericProperty(5)
  mode = StringProperty('')
  current_seq  = StringProperty('')
  current_pose = StringProperty('')
  is_start = BooleanProperty(False)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.score_acc = 0
    self.attempt_acc = 0
    global preparation_time
    self.time_acc = preparation_time

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
    if exists(self.ids['reference_image'].source):
      self.ids['reference_image'].reload()
      self.current_seq  = seq_id
      self.current_pose = pos_id
      return True
    else:
      return False

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

  def start_stop_button(self):
    self.is_start = not self.is_start

    if(self.is_start == True):
      self.ids['score_label'].text = "Follow the reference..."
      self.start_training()
      self.ids.start_button.text = 'Stop'
    else:
      # self.is_start == False
      self.ids['score_label'].text = "Press Start to Continue"
      self.set_preparation_countdown()
      self.ids.start_button.text = 'Start'
      self.stop_countdown()

  def stop_countdown(self):
    self.anim.cancel(self)

  def set_preparation_countdown(self):
    # Ray: set the value for the countdown timer for preparation phase
    self.countdown = preparation_time

  def set_move_on_countdown(self):
    # Ray: set the value for the countdown timer for move on phase
    self.countdown = move_on_time

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
      line_width = 6
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
    
    return (all_x[8], all_y[8])

  def draw_user_skeleton(self, pose_coords, ref_waist_pos, checklist, missing_joints):
    if (len(missing_joints) > 0):
      print("not drawing all skeletons due to player not fully in screen")
      return
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

    cur_user_waist_x = all_x[8]
    cur_user_waist_y = all_y[8]
    
    all_x = all_x - cur_user_waist_x + ref_waist_pos[0]
    all_y = all_y - cur_user_waist_y + ref_waist_pos[1]

    # Start drawing
    with self.ids.skeleton_canvas.canvas:
      # Draw the user pose

      # Go through all limbs
      line_width = 6
      head_radius = 40
      
      # Torso -> Right Arm Top
      if checklist[1]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[1], all_y[1], all_x[2], all_y[2]], width=line_width)
      
      # Right Arm Top -> Right Arm Middle
      if checklist[2]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[2], all_y[2], all_x[3], all_y[3]], width=line_width)
      
      # Right Arm Middle -> Right Hand
      if checklist[3]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[3], all_y[3], all_x[4], all_y[4]], width=line_width)
      
      # Torso -> Left Arm Top
      if checklist[4]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[1], all_y[1], all_x[5], all_y[5]], width=line_width)
      
      # Left Arm Top -> Left Arm Middle
      if checklist[5]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red      
      Line(points=[all_x[5], all_y[5], all_x[6], all_y[6]], width=line_width)
      
      # Left Arm Middle -> Left Hand
      if checklist[6]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[6], all_y[6], all_x[7], all_y[7]], width=line_width)
      
      # Torso -> Waist
      if checklist[7]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[1], all_y[1], all_x[8], all_y[8]], width=line_width)
      
      # Waist -> Right Leg Top
      if checklist[8]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red      
      Line(points=[all_x[8], all_y[8], all_x[9], all_y[9]], width=line_width)
      
      # Right Leg Top -> Right Leg Middle
      if checklist[9]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[9], all_y[9], all_x[10], all_y[10]], width=line_width)
      
      # Right Leg Middle -> Right Foot
      if checklist[10]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[10], all_y[10], all_x[11], all_y[11]], width=line_width)
      
      # Waist -> Left Leg Top
      if checklist[11]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[8], all_y[8], all_x[12], all_y[12]], width=line_width)
      
      # Left Leg Top -> Left Leg Middle
      if checklist[12]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[12], all_y[12], all_x[13], all_y[13]], width=line_width)
      
      # Left Leg Middle -> Left Foot
      if checklist[13]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[13], all_y[13], all_x[14], all_y[14]], width=line_width)
      
      # Left Foot -> Left Toe
      if checklist[14]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[14], all_y[14], all_x[19], all_y[19]], width=line_width)
      
      # Right Foot -> Right Toe
      if checklist[15]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[11], all_y[11], all_x[22], all_y[22]], width=line_width)
      
      # Head -> Torso
      if checklist[0]:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Line(points=[all_x[0], all_y[0], all_x[1], all_y[1]], width=line_width)
      
      
      Ellipse(pos=(all_x[0] - head_radius, all_y[0] - head_radius), size=(head_radius * 2, head_radius * 2))
    pass

  def remove_user_pic(self):
    if (os.path.exists(join('.', 'user_input', 'user.png'))):
      remove(join('.', 'user_input', 'user.png'))

  def move_on(self):
    print("move_on() called")
    global tolerance
    joint_data = backend_process(self.mode, self.current_seq, self.current_pose, tolerance)
    
    if len(joint_data) == 1:
      # Error! Switch to result screen
      print("Error encountered")
      self.is_start = False
      self.remove_user_pic()
      self.manager.get_screen('result').ids['average_score'].text = joint_data[0]
      self.manager.get_screen('result').ids['total_time'].text = ''
      self.manager.get_screen('result').ids['tips_label'].text = ''
      self.manager.current = 'result'
      return

      # return
    # Drawing pipeline
    # Extract all joint data
    pose_pass = joint_data[0]
    reference_pose_coords = joint_data[1]
    user_pose_coords = joint_data[2]
    limb_checklist = joint_data[3]
    user_score = ceil(joint_data[4] * 100)
    missing_joints = joint_data[5]

    # Clear skeleton canvas
    canvas_to_draw = self.ids.skeleton_canvas
    canvas_to_draw.canvas.clear()  

    # Show Signal
    with canvas_to_draw.canvas:
      if pose_pass:
        Color(0, 1, 0, 1) # Correct in Green
      else:
        Color(1, 0, 0, 1) # Wrong in Red
      Rectangle(pos=(0, 0), size=(canvas_to_draw.width, canvas_to_draw.height))
      Color(0, 0, 0, 1) # Background in Black
      Rectangle(pos=(10, 10), size=(canvas_to_draw.width - 20, canvas_to_draw.height - 20))

    # Draw poses  
    ref_waist_pos = self.draw_reference_skeleton(reference_pose_coords)
    self.draw_user_skeleton(user_pose_coords, ref_waist_pos, limb_checklist, missing_joints)

    # accumulate score and attempt
    self.score_acc += user_score
    self.attempt_acc += 1

    print("Skeleton drawn, Score accumulated")

    # Check back_process return
    if all(limb_checklist) and user_score >= 90:
      self.current_pose = str(int(self.current_pose) + 1)
      next_pose_exists = self.set_reference_image(self.mode, self.current_seq, self.current_pose)
      if next_pose_exists:
        # Display new reference and user skelectons with correct body part
        # Verbal instruction reading "great job"
        self.ids['score_label'].text = f'Score: {user_score}! Keep it up!'

        # Set up countdown timer here with move on interval
        self.set_move_on_countdown()
        self.start_training()
        print("Next pose exists")
      else:
        # Training Over! Switch to result screen
        self.is_start = False
        self.remove_user_pic()
        self.manager.get_screen('result').ids['average_score'].text = f'Your Final Score: {ceil(self.score_acc / self.attempt_acc)}'
        self.manager.get_screen('result').ids['total_time'].text = f'Total Training Time: {ceil(self.time_acc)}s'
        self.manager.get_screen('result').ids['tips_label'].text = f'Tip: {choice(tips)}'
        self.manager.current = 'result'
        print("Next pose does not exist")
    else:
      # Switch reference image to next pose using set_reference_image()
      # Display new reference and user skelectons with correct body part
      # Verbal instruction reading "great job"
      self.ids['score_label'].text = f'Score: {user_score}. You can do it!'

      # Set up countdown timer here with move on interval
      self.set_move_on_countdown()
      self.start_training()
      print("Score too low")
    
    # accumulate total training time
    global move_on_time
    self.time_acc += move_on_time
    print("time accumulated")

  def on_countdown(self, instance, value):
    # Ray: this is for animation of the start button text
    #      it starts with "on" for a purpose: to match weired kivy syntax
    #      don't call it in any function in this class
    #      don't call it in any function in this class
    #      don't call it in any function in this class
    start_button = self.ids['start_button']
    start_button.text = str(round(value, 1))

# trimmed camera, used in training screen
class TrimmedCamera(Camera):
  # https://stackoverflow.com/questions/67967041/how-can-i-use-kivy-to-zoom-in-or-zoom-out-live-camera
  region_x = NumericProperty(200)
  region_y = NumericProperty(0)
  region_w = NumericProperty(320)
  region_h = NumericProperty(480)
  
  def on_tex(self, camera):
    self.texture = texture = camera.texture
    # get some region
    self.texture = self.texture.get_region(self.region_x, self.region_y, self.region_w, self.region_h)
    self.texture_size = list(texture.size)
    self.canvas.ask_update()

# result screen
class ResultScreen(Screen):
  pass

# custom screen
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

# pose sequence item, used in custom screen
class PoseSequenceItem(Widget):
  pass

# confirm screen
class ConfirmScreen(Screen):

  def __init__(self, **kwargs):
    super(ConfirmScreen, self).__init__(**kwargs)
    self.filename = ""
    self.curr_dir = getcwd()
    self.new_filename = ""
    self.display_label = None
    self.posesList = []
    self.filenameList = []
    self.poseLabel = ""
    # self.existing_custom_poses_list = []
    self.num_custom_poses = 0
    # self.textbox = None
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

    # self.existing_custom_poses_list = os.listdir(f"{self.curr_dir}\\user_poses\\")

    self.num_custom_poses = len(os.listdir(f"{self.curr_dir}\\user_poses\\"))
    
    # print("self.existing_custom_poses_list", self.existing_custom_poses_list)
    # print("number of custom poses = ", len(self.existing_custom_poses_list))
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

  def ch_back_dir(self):
    os.chdir(self.curr_dir)

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
    src.reverse()
    dest = []

    pose_folder_path = ""
    # print("self.curr_dir: ", self.curr_dir)
    
    # for i in range(len(src)):
    pose_folder_path = f"{self.curr_dir}\\user_poses\\{self.num_custom_poses + 1} - {self.poseLabel}"

    mkdir_status = system(f'mkdir "{self.curr_dir}\\user_poses\\{self.num_custom_poses + 1} - {self.poseLabel}"')
    print("mkdir_status = ", mkdir_status)
    print("system_cmd: ", repr(f"mkdir {pose_folder_path}") )

    for i in range(len(src)):

      filename, filetype = getFileTypeAndName(src[i]) 
    
      if(self.new_filename != ""):
        filename = self.new_filename

      # print("   src_path  : ", src_path
      
      dest.append(f"{pose_folder_path}\\{i}.{filetype}")
      
    # print("src: ", src)
    for j in range(len(dest)):
      if os.name == 'nt':  # Windows
        print("dest[j]: ", dest[j])
        cmd = f'copy "{src[j]}" "{dest[j]}"'
      else:  # Unix/Linux
        cmd.replace("\\", "/")
        cmd = f'cp "{src}" "{dst}"'
      print("cmd: ", repr(cmd))
      system(cmd)
      
      # print("src: ", src[j])
      # print("dest: ", dest[j])
    print("self.curr_dir: ", self.curr_dir)
    self.ch_back_dir()
    main_curr_dir = getcwd()
    print("main_curr_dir: ", main_curr_dir)
    os.mkdir(f"{pose_folder_path}\\ref_coords")
    # print("pose_folder_path", pose_folder_path)
    parseImageFromPath(f'"{pose_folder_path}"', f'"{pose_folder_path}\\ref_coords"')
    self.posesList = []
    self.ids.grid_layout.clear_widgets()
    self.remove_widget(self.display_label)
    print("done")

    # self.on_enter = on_enter()

# swap two elements in a list
def swap(list, indexA, indexB):
  temp = list[indexA]
  list[indexA] = list[indexB]
  list[indexB] = temp

# get the file type and name from the file source
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

# Tutorial screen
class TutorialScreen(Screen):
  pass

# actual app
class TaichineApp(App):
  pass 

if __name__ == '__main__':
  TaichineApp().run()