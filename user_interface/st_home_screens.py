"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: Student and Teacher Home Screens
"""
import os
import kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

from kivy.properties import ObjectProperty, StringProperty
import pickle

from user_interface.global_variables import *
from user_interface.student_topic import StudentTopic
from user_interface.teacher_topic import TeacherTopic

file_path = os.path.join(design_path, 'st_home_screens.kv')
Builder.load_file(file_path)


class StudentTopicsRV(RecycleView):
    
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # from user_interface.topic_screen import TopicScreen
        self.data = [{'text': topic, 'on_press': partial(self.get_topic, topic)} for topic in topics]

    
    def get_topic(self, topic):
        topic_screen = StudentTopic(name='student_topic',topic=topic)
        sm.add_widget(topic_screen)
        sm.current = 'student_topic'


class StudentScreen(Screen):
    def __init__(self, **kwargs):
        super(StudentScreen, self).__init__(**kwargs)
        StudentTopicsRV()
        

class TeacherTopicsRV(RecycleView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.data = [{'text': topic, 'on_press': partial(self.get_topic, topic)} for topic in topics]

    def get_topic(self, topic):
        
        topic_screen = TeacherTopic(name='teacher_topic',topic=topic)
        sm.add_widget(topic_screen)
        sm.current = 'teacher_topic'


class TeacherScreen(Screen):
    def __init__(self, **kwargs):
        super(TeacherScreen, self).__init__(**kwargs)
        TeacherTopicsRV()