from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
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
      self.file_label = ""
      print("self.curr_dir: ", self.curr_dir)
      super().__init__(**kwargs)

    def select_file(self):
      system(f"mkdir {self.poses_folder}")
      filechooser.open_file(on_selection = self.selected)
    
    def selected(self, selection):
        
      src = selection
      globals()['confirm_selection'] = src
      print("globals()['confirm_selection']: ", globals()["confirm_selection"])
      # dest = []
      # print("self.curr_dir: ", self.curr_dir)
      
      # for i in range(len(src)):
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
    
    for i in range(len(src)):
      

      # removing old filename from path
      filename, filetype = getFileTypeAndName(src[i]) # = src_split_list.pop(-1)
      # join_char = "\\"
      # src_path = join_char.join(src_split_list)
      
      if(self.new_filename != ""):
        filename = self.new_filename

      # print("   src_path  : ", src_path)
      system(f"mkdir {self.curr_dir}\\user_poses\\{filename}")
      dest.append(f"{self.curr_dir}\\user_poses\\{filename}\\{filename}.{filetype}")
      
    print("src: ", src)
    for j in range(len(dest)):
      if os.name == 'nt':  # Windows
        cmd = f'copy "{src[j]}" "{dest[j]}"'
      else:  # Unix/Linux
        cmd.replace("\\", "/")
        cmd = f'cp "{src}" "{dst}"'
      print(repr(cmd))
      system(cmd)
      print("src: ", src[j])
      print("dest: ", dest[j])
    # print(selection[0])

    print("done")

    # self.on_enter = on_enter()
    

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