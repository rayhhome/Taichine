from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.core.window import Window
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