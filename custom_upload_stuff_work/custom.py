import kivy
# from "..\\openpose_env\\openpose\\openpose_inter.py" import parseImageFromPath
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
from kivy.core.window import Window

import os

#
# TODO: edit folder to use poses
# 

Builder.load_file("upload_button.kv")

# class upload_image_widget(Screen):
    
    
#         # print(self.parent)
#     pass

class PoseSequenceItem(RelativeLayout):
    # def exit_button(self):
    #     print("\n\nEXIT button pressed!\n\n")

    # def left_button(self):
    #     print("\n\nLEFT button pressed!\n\n")

    # def right_button(self):
    #     print("\n\nRIGHT button pressed!\n\n")
    # for children in self.children:
    #     print(children)
    pass


class upload_layout(Screen):

    def __init__(self, **kwargs):
        self.curr_dir = curr_dir = os.getcwd()
        self.poses_folder = f"{curr_dir}\\poses"
        print("self.curr_dir: ", self.curr_dir)
        super().__init__(**kwargs)

    
    def on_pre_enter(self, *largs):
        # dest = []
        # print("self.curr_dir: ", self.curr_dir)
        
        # for i in range(len(selection)):
        #     src_split_list = src[i].split('\\')
        #     filename = src_split_list[-1] 
        #     dest.append(f"{self.curr_dir}\\poses\\{filename}")

        
        # for j in range(len(dest)):
        #     cmd = f'copy "{src[j]}" "{dest[j]}"'
        #     print("src: ", src[j])
        #     print("dest: ", dest[j])
        #     os.system(cmd)
        # print(selection[0])
        grid_layout = GridLayout(rows=1, orientation='lr-tb', padding=5, size_hint={1, 0.7}, pos_hint={'center_x': 0.5,'center_y': 0.5})
        self.add_widget(grid_layout)
        print("grid_layout.height = ", grid_layout.height)
        print("grid_layout.width = ", grid_layout.width)
        # for i in range(1):
        pose_item1 = PoseSequenceItem()
        pose_item2 = PoseSequenceItem()
        pose_item3 = PoseSequenceItem()
        pose_item4 = PoseSequenceItem()
        pose_item5 = PoseSequenceItem()
        # image1 = Image(source='icons/no_image_96.png')
        # image2 = Image(source='icons/no_image_96.png')
        # pose_item.ids.pose_image.source = self.posesList[i]
        # grid_layout.add_widget(image1)
        # grid_layout.add_widget(image2)
        # grid_layout.add_widget(Button())
        grid_layout.add_widget(pose_item1)
        grid_layout.add_widget(pose_item2)
        grid_layout.add_widget(pose_item3)
        grid_layout.add_widget(pose_item4)
        grid_layout.add_widget(pose_item5)



class customApp(App):

    def build(self):

        sm = ScreenManager(transition=NoTransition())
        
        sm.add_widget(upload_layout())
        # sm.add_widget(upload_image_widget())
        return sm
        # return upload_layout()
    
    
    
if __name__ == '__main__':
    
    customApp().run()

