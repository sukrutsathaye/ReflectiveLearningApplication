"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: global variables
"""
from functools import partial
import kivy
import os
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder



sm = ScreenManager()
# root_path = os.path.abspath(os.path.abspath(__file__))
root_path = os.path.dirname(os.path.abspath(__file__))
design_path = os.path.join(root_path, 'Design')
parent_path = os.path.dirname(root_path)
topic_path = os.path.join(parent_path, 'Topics')
print("Parent_path: ", parent_path)
print("Topic_path",topic_path)
print("Root Path",root_path)
# print("Topics: ",topics)
topics = os.listdir(topic_path)
global chapters_read

chapters_read = 0


    # def choose_topic(self, instance):
    #     print("Topic Selected: ", instance.text)
