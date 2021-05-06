"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: Teacher Screen
"""
import os
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.recycleview import RecycleView
import pickle
from functools import partial

from user_interface.global_variables import *

file_path = os.path.join(design_path, 'teacher_screen.kv')
Builder.load_file(file_path)

class RVTeacher(RecycleView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.data = [{'text': topic, 'on_press': partial(self.get_topic, topic)} for topic in topics]

    def get_topic(self, topic):
        from user_interface.teacher_topic import TeacherTopic
        topic_screen = TeacherTopic(name='teacher_topic',topic=topic)
        sm.add_widget(topic_screen)
        sm.current = 'teacher_topic'

class TeacherScreen(Screen):
    def __init__(self, **kwargs):
        super(TeacherScreen, self).__init__(**kwargs)
        # teacher_selection = ObjectProperty(None)
        # status = ObjectProperty(None)
        RVTeacher()


    def select_topic(self):
        topic_id = self.teacher_selection.text
        # print("Teacher Selection: ", topic_id)
        if not topic_id.isnumeric():
            self.status.text = 'Invalid entry only select numbers from list above!'
        for srno, topic in enumerate(topics):
            if topic_id == str(srno):
                ckw_screen = CorrectKWScreen(name='c_kw', topic=topic)
                sm.add_widget(ckw_screen)
                sm.current = 'c_kw'



