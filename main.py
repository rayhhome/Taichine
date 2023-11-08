from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.textinput import TextInput 
from kivy.properties import ObjectProperty
from plyer import filechooser
from os import system, getcwd
from os import listdir
from os.path import join, isfile
import os

confirm_selection = None
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
  pass

# setting screen
class SettingScreen(Screen):
  pass

# training screen
class TrainingScreen(Screen):
  pass

class CustomScreen(Screen):

    def __init__(self, **kwargs):
        self.curr_dir = curr_dir = getcwd()
        self.poses_folder = f"{curr_dir}\\user_poses"
        print("self.curr_dir: ", self.curr_dir)
        super().__init__(**kwargs)

    def select_file(self):
        system(f"mkdir {self.poses_folder}")
        filechooser.open_file(on_selection = self.selected)
    
    def selected(self, selection):
        
      src = selection
      globals()['confirm_selection'] = src[0]
      print("globals()['confirm_selection']: ", globals()["confirm_selection"])
      dest = []
      print("self.curr_dir: ", self.curr_dir)
      
      for i in range(len(selection)):
          src_split_list = src[i].split('\\')
          filename = src_split_list[-1] 
          dest.append(f"{self.curr_dir}\\user_poses\\{filename}")
      
      print("src: ", src)
      for j in range(len(dest)):
        if os.name == 'nt':  # Windows
          cmd = f'copy "{src[j]}" "{dest[j]}"'
        else:  # Unix/Linux
          cmd.replace("\\", "/")
          cmd = f'cp "{src}" "{dst}"'
          
        print("src: ", src[j])
        print("dest: ", dest[j])
        system(cmd)
      # print(selection[0])
  
      print("done")

class ConfirmScreen(Screen):

  def __init__(self, **kwargs):

    super(ConfirmScreen, self).__init__(**kwargs)
    self.filename=""
    # self.textbox = None
  
  

  def on_pre_enter(self, *largs):
    
    # print("new screen globals()['confirm_selection']: ", globals()['confirm_selection'])
    #  height=30,
    def on_enter(instance): #, value
      print("value: ", instance.text)
    # self.on_enter = on_enter()
    textbox = TextInput(size_hint=(0.3, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.7}, cursor_blink=True, multiline=False)
    textbox.bind(on_text_validate=on_enter)
    self.add_widget(textbox)
    src_split_list = confirm_selection.split('\\')
    filename = src_split_list[-1]
    # print("filename: ", filename)
    self.display_image = Image(source=confirm_selection, size_hint=(0.3, 0.3), pos_hint={'center_x': 0.5, 'center_y': 0.4})
    self.add_widget(self.display_image)

class TaichineApp(App):
  def build(self):
    Window.minimum_width, Window.minimum_height = (800, 600)    
    smanager = ScreenManager()
    smanager.add_widget(MenuScreen())
    smanager.add_widget(SelectionScreen())
    smanager.add_widget(SettingScreen())
    smanager.add_widget(TrainingScreen())
    smanager.add_widget(CustomScreen())
    smanager.add_widget(ConfirmScreen())
    # allseqs = listdir('./poses')
    # for seq in allseqs:
    #   if isfile(join('./poses', seq)):
    #     pose = PoseItem()
    #     pose.id = seq
    #     pose.image = './poses/' + seq + '/0.jpg'
    #     pose.label = seq
    #     smanager.add_widget(pose)
    return smanager
    
if __name__ == '__main__':
  TaichineApp().run()