"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: Main Screen
"""
import os
import kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
import pickle
import pprint

from user_interface.global_variables import *
from user_interface.st_home_screens import StudentScreen, TeacherScreen
from source_code.ReflectiveLearningV7 import QuestionAnswerGenerator as qag
from source_code.ReflectiveLearningV7 import TestOptionGen as testoptn
from source_code.ReflectiveLearningV7 import NewTopicCreator as ntc
from source_code.ReflectiveLearningV7 import ExtractKeyWords as ekw


file_path = os.path.join(design_path, 'main_screen.kv')
Builder.load_file(file_path)


class MainScreen(Screen):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        login_id = ObjectProperty(None)
        password = ObjectProperty(None)
        status = ObjectProperty(None)
        self.registered_users = {
            # need to keep complete names in production
            's'      : '1',
            't'      : 'a',
            'a'      : 'q'
            }
        self.add_screens()


    def add_screens(self):
        student_screen = StudentScreen(name='student')
        sm.add_widget(student_screen)
        teacher_screen = TeacherScreen(name='teacher')
        sm.add_widget(teacher_screen)
        admin_screen = AdminScreen(name='admin')
        sm.add_widget(admin_screen)


    def user_login(self):
        user = self.login_id.text
        password = self.password.text
        if user not in list(self.registered_users.keys()):
            self.status.text = 'Unregistered User'
            self.login_id.text = ''
            self.password.text = ''
        else:
            if user == 's': # student
                if password == self.registered_users[user]:
                    self.status.text = 'Logged in as Student'
                    sm.current = 'student'
                else:
                    self.status.text = 'Invalid Password try again'
                    self.password.text = ''
            elif user == 't': # teacher
                if password == self.registered_users[user]:
                    self.status.text = 'Logged in as Teacher'
                    sm.current = 'teacher'
                else:
                    self.status.text = 'Invalid Password try again'
                    self.password.text = ''
            elif user == 'a':
                if password == self.registered_users[user]:
                    sm.current = 'admin'
                else:
                    self.status.text = 'Invalid Password try again'
                    self.password.text = ''


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super(AdminScreen, self).__init__(**kwargs)
        topic = ObjectProperty(None)
        status = ObjectProperty(None)


    def add_new_topic(self):
        # topic = self.new_topic.text
        if not self.topic.text.isnumeric():
            print("Existing Topics: ", topics)
            if self.topic.text not in topics:
                print("Adding new topic")
                adder = ntc(self.topic.text)
                self.status.text = 'Done'
            else:
                self.status.text = 'Topic already exists, add a different topic'
                self.topic.text = ''
        else:
            self.status.text = 'Invalid topic, please re-enter'
            self.topic.text = ''
            
            
    def debug(self):
        ds = DebugScreen(name='ds', topic=self.topic.text)
        sm.add_widget(ds)
        sm.current = 'ds'
        
        
        
class DebugScreen(Screen):
    def __init__(self, topic, **kwargs):
        super(DebugScreen, self).__init__(**kwargs)
        self.topic = topic
        
        
    def compare_keywords(self):
        obj = ekw(self.topic)
        comp_kw = obj.compare_keywords(per_parra=True)
        pprint.pprint(comp_kw, indent=2,width= 100)
        
        
    def back(self):
        sm.current = 'admin'