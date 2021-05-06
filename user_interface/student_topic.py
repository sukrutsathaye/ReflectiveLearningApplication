"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: Student Screen
"""

import os
import kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from user_interface.global_variables import *
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
import pickle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from user_interface.question_answer_screen import QuestionAnswerScreen, SubjectiveQuestionScreen
file_path = os.path.join(design_path, 'student_topic.kv')
Builder.load_file(file_path)


class StudentTopic(Screen):
    def __init__(self,topic, **kwargs):
        super(StudentTopic, self).__init__(**kwargs)
        # set up object Properties
        topic_heading = ObjectProperty(None)
        topic_text = ObjectProperty(None)
        scroll = NumericProperty(1)
        previous_btn = ObjectProperty(None)
        next_btn = ObjectProperty(None)
        # subjective_question_btn = ObjectProperty(None)
        # rl = ReflectiveLearningBackend(topic)
        self.topic = topic
        self.is_file = False
        self.one_chapter = 10
        self.is_last_chapter = False
        fpath = os.path.join(topic_path, topic)
        files = os.listdir(fpath)

        if 'text.pkl' in files:
            self.is_file = True
            file_name = os.path.join(fpath, 'text.pkl')
            with open(file_name, 'rb') as f:
                self.text_per_parra = pickle.load(f)
        else:
            print("Create and save text")
            self.text_per_parra = rl.qag.clean_text()
        # Change this line in production, because this displays 10 paras only.
        # self.text_per_parra = self.text_per_parra[:10]
        self.disp_counter = 0
        self.update_label_new()


    def disp_next(self, instance):
        if self.disp_counter < len(self.text_per_parra):
            self.disp_counter += 1
        self.update_label_new()


    def disp_previous(self, instance):
        # if self.disp_counter == 0:
        #     instance.disabled = True
        # else:
        #     instance.disabled = False
        if self.disp_counter > 0:
            self.disp_counter -= 1
        self.update_label_new()


    def disp_subjective_questions(self, instance):

        # if chapters_read > len(self.text_per_parra)/2:
        #     instance.disabled = False
        sub_questions = SubjectiveQuestionScreen(name='sub_q', topic=self.topic)
        sm.add_widget(sub_questions)
        sm.current = 'sub_q'


    def show_popup(self):
        show = PopUpQues(topic=self.topic)
        global popupWindow
        popupWindow = Popup(title ="Get Questions", content = show,
                        size_hint =(None, None), size =(300, 300))
        popupWindow.open()


    def update_label(self):
        global chapters_read
        if self.is_file:
            # print("Display Counter: ", self.disp_counter)
            # print("Chapters Read: ", chapters_read)
            # # this condition can be changed later
            # if chapters_read >= 5:
            #     self.subjective_question_btn.disabled = False
            # else:
            #     self.subjective_question_btn.disabled = True
            sents_counter = 0
            if self.disp_counter == 0:
                chapters_read = 1
            elif self.disp_counter > chapters_read - 1:
                chapters_read = self.disp_counter + 1
            if self.disp_counter < len(self.text_per_parra):
                self.topic_text.text = self.text_per_parra[self.disp_counter]
                sentences = self.text_per_parra[self.disp_counter].split(sep='.')
                sents_counter = len(sentences)
            else:
                self.topic_text.text = "You have reached to the end of this topic.\nTry some questions?"
        else:
            self.topic_text.text = "Text is not available at the moment, it is\nbeing generated. Please wait."


    def update_label_new(self):
        self.scroll.scroll_y = 1
        global chapters_read
        # chapters_read = 0
        if self.disp_counter == 0:
            self.previous_btn.disabled = True
            if chapters_read <= 10:
                chapters_read = 10
        else:
            self.previous_btn.disabled = False
            if not self.is_last_chapter:
                if chapters_read <= 10*(self.disp_counter + 1):
                    chapters_read = 10*(self.disp_counter + 1)
            else:
                chapters_read = len(self.text_per_parra)
        # elif self.disp_counter > chapters_read - 1:
        #     chapters_read = self.disp_counter + 1
        self.topic_heading.text = f'Topic : {self.topic}'
        one_chap_text = ''
        # print("Chp. read: ", chapters_read, '\ndisp counter: ', self.disp_counter)
        start_val = self.disp_counter*self.one_chapter
        fin_val = (self.disp_counter + 1)*self.one_chapter
        if fin_val < len(self.text_per_parra):
            self.is_last_chapter = False
            for text in self.text_per_parra[start_val:fin_val]:
                one_chap_text += text + '\n\n'
        else:
            chapters_read = len(self.text_per_parra)
            # print("Chp. read: ", chapters_read, '\ndisp counter: ', self.disp_counter)
            for text in self.text_per_parra[start_val:len(self.text_per_parra)]:
                one_chap_text += text + '\n\n'
            self.is_last_chapter = True
        if not self.is_last_chapter:
            self.topic_text.text = one_chap_text
            self.next_btn.disabled = False
        else:
            self.topic_text.text = "You have reached to the end of this topic.\nTry some questions?"
            self.next_btn.disabled = True
            


class PopUpQues(GridLayout):
    def __init__(self, topic, **kwargs):
        super(PopUpQues, self).__init__(**kwargs)
        no_of_ques = ObjectProperty(None)
        self.topic = topic


    def get_no_questions(self):
        ques = self.no_of_ques.text
        print("No of ques selected: ", ques)
        global popupWindow
        popupWindow.dismiss()
        ques_screen = QuestionAnswerScreen(name='qas',
            topic=self.topic, n_of_ques=ques, chap_read=chapters_read)
        sm.add_widget(ques_screen)
        sm.current = 'qas'
