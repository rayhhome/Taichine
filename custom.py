import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
# from kivy.uix.filechooser import FileChooser
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.core import window
from kivy.uix.label import Label
from plyer import filechooser
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import StringProperty

import os

#
# TODO:
# Architect File Chooser Icon View thing
#

Builder.load_file("upload_button.kv")

class upload_image_widget(Screen):
    
    def exit_button(self):
        print("\n\nEXIT button pressed!\n\n")

    def left_button(self):
        print("\n\nLEFT button pressed!\n\n")

    def right_button(self):
        print("\n\nRIGHT button pressed!\n\n")

    pass


class upload_layout(Screen):

    def __init__(self, **kwargs):
        self.curr_dir = curr_dir = os.getcwd()
        self.poses_folder = f"{curr_dir}\\user_poses"
        print("self.curr_dir: ", self.curr_dir)
        super().__init__(**kwargs)

    def select_file(self):
        os.system(f"mkdir {self.poses_folder}")
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
            os.system(cmd)
        # print(selection[0])
    
        print("done")

   


class customApp(App):

    def build(self):

        sm = ScreenManager(transition=NoTransition())
        
        sm.add_widget(upload_layout())
        sm.add_widget(upload_image_widget())
        return sm
        # return upload_layout()
    
    
    
if __name__ == '__main__':
    
    customApp().run()

