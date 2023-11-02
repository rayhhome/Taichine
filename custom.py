import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
# from kivy.uix.filechooser import FileChooser
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.core import window
from kivy.uix.label import Label
from plyer import filechooser

import os

#
# TODO:
# Architect File Chooser Icon View thing
#

Builder.load_file("upload_button.kv")

class File_choose_popup(Widget):

    def selected(self, filepath, filename):
        try:
            self.File_choose_widget.file_path = filename[0]
            src = filename[0]
            path = filepath[0]
            
            # if os.name == 'nt':  # Windows
            #     cmd = f'copy "{src}" "{dst}"'
            # else:  # Unix/Linux
            #     cmd = f'cp "{src}" "{dst}"'
        except:
            popup = Popup(title='Upload Failed',
                      content=Label(text='Hello world'),
                      size_hint=(None, None), size=(400, 400))
            popup.open()



class upload_layout(Widget):

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
            dest.append(f"{self.curr_dir}\\user_poses\\pose_{i}.png")

        
        for j in range(len(dest)):
            cmd = f'copy "{src[j]}" "{dest[j]}"'
            print("src: ", src[j])
            print("dest: ", dest[j])
            os.system(cmd)
        # print(selection[0])
        print("done")

   


class customApp(App):

    def build(self):
        
        return upload_layout()
    
    
    
if __name__ == '__main__':
    
    customApp().run()

