# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 15:15:08 2021

@author: sukrut
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

from user_interface.global_variables import *
from user_interface.main_screen import MainScreen

class ReflectiveLearningApp(App):


    def build(self):
        screen = MainScreen(name='main')
        sm.add_widget(screen)
        sm.current = 'main'
        return sm

    # def on_request_close(self, *args):
    #     print("Save all global variables for better efficiency.")

if __name__ == '__main__':
    ReflectiveLearningApp().run()