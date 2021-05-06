import os
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
import copy
import pickle

from user_interface.global_variables import *

file_path = os.path.join(design_path, 'teacher_topic.kv')
Builder.load_file(file_path)


class TeacherTopic(Screen):
    def __init__(self, topic, **kwargs):
        super(TeacherTopic, self).__init__(**kwargs)
        self.topic = topic
        self.topic_path = os.path.join(topic_path, topic)
        disp_ques = DispQuestions(name='disp_ques_teacher', topic=topic)
        sm.add_widget(disp_ques)


    def correct_kw(self):
        print("Launch Correct Kw Screen")
        correct_kw_screen = CorrectKWScreen(name='c_kw', topic=self.topic)
        sm.add_widget(correct_kw_screen)
        sm.current = 'c_kw'


    def view_ques(self):
        print("Display Questions in Scroll View")
        sm.current = 'disp_ques_teacher'



    def correct_ques(self):
        print("Correct Subjective Questions")
        file_name = os.path.join(self.topic_path, 'subj_questions.pkl')
        correct_sq_screen = CorrectSQScreen(name='csq', topic=self.topic)
        sm.add_widget(correct_sq_screen)
        sm.current = 'csq'

    def exit_program(self):
        print("Exiting Application")
        App.get_running_app().stop()
        
        
class CorrectSQScreen(Screen):
    def __init__(self, topic, **kwargs):
        super(CorrectSQScreen, self).__init__(**kwargs)
        self.disp_counter = 0
        self.topic = topic
        self.topic_path = os.path.join(topic_path, topic)
        self.approved_ques = []
        # self.subj_questions = []
        # set Object Properties
        file_name = os.path.join(self.topic_path, 'subj_questions.pkl')
        with open(file_name, 'rb') as f:
            self.subj_questions = pickle.load(f)
        # for kw, sub_q in kw_subq_list:
        #     self.subj_questions.append(sub_q)
        # print("Subj Ques: ", self.subj_questions)
        disp_q = ObjectProperty(None)
        text_inpt = ObjectProperty(None)
        approve_btn = ObjectProperty(None)
        disapprove_btn = ObjectProperty(None)
        back_btn = ObjectProperty(None)
        self.update_screen()
        
        
    def back(self):
        sm.current = 'teacher_topic'
    
    def update_screen(self):
        self.text_inpt.text = ''
        if self.disp_counter < len(self.subj_questions):
            self.back_btn.disabled = True
            self.disp_q.text = self.subj_questions[self.disp_counter][1]
        else:
            file_name = os.path.join(self.topic_path, 'csubj_questions.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(self.approved_ques, f)
            self.disp_q.text = 'All questions are corrected'
            self.approve_btn.disabled = True
            self.disapprove_btn.disabled = True
            self.back_btn.disabled = False
        
        
    def approved_question(self):
        self.approved_ques.append(self.subj_questions[self.disp_counter])
        self.disp_counter += 1
        self.update_screen()
        
        
    def disapproved_question(self):
        if self.text_inpt.text != '':
            kw = self.subj_questions[self.disp_counter][0]
            self.approved_ques.append((kw, self.text_inpt.text))
        self.disp_counter += 1
        self.update_screen()
        
        

    
class CorrectKWScreen(Screen):
    def __init__(self, topic, **kwargs):
        super(CorrectKWScreen, self).__init__(**kwargs)
        # define object Properties
        self.topic = topic
        topic_name = ObjectProperty(None)
        keyword = ObjectProperty(None)
        correct_answer = ObjectProperty(None)
        total_keywords = ObjectProperty(None)
        correct_btn = ObjectProperty(None)
        incorrect_btn = ObjectProperty(None)
        # set up basic important variables
        self.topic_path = os.path.join(topic_path, topic)
        self.files = os.listdir(self.topic_path)
        self.srno = 0
        self.all_keywords = self.get_all_keywords()
        self.is_evaluation = False
        if 'unchecked_kw.pkl' not in self.files and 'checked_kw.pkl' not in self.files:
            print("Ich bin hier!!!!!!")
            self.updated_unchecked = copy.deepcopy(self.all_keywords)
        if 'unchecked_kw.pkl' in self.files:
            print("Now here!!!!")
            file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
            with open(file_name, 'rb') as f:
                self.updated_unchecked = pickle.load(f)
        # print(self.updated_unchecked)
        self.correct_kw = []
        self.display_keyword()
        if 'correct_kw.pkl' not in self.files:
            # keywords not yet completely corrected
            if 'checked_kw.pkl' not in self.files:
                # keyword correction not started
                file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.all_keywords, f)
            else:
                # keywords partially checked.
                # checked_kw.pkl and unchecked_kw.pkl should exist.
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    self.already_checked = pickle.load(f)
                file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
                with open(file_name, 'rb') as f:
                    self.updated_unchecked = pickle.load(f)
                    # print("Updated unchecked: ", self.updated_unchecked)
        else:
            self.evaluation_result()
        
        
    def get_all_keywords(self):
        file_name = os.path.join(self.topic_path, 'keywords.pkl')
        with open(file_name, 'rb') as f:
            kw_per_parra = pickle.load(f)
        all_keywords = []
        for kw_list in kw_per_parra:
            for kw in kw_list:
                all_keywords.append(kw)
        return list(set(all_keywords))
    
    
    def evaluation_result(self):
        self.is_evaluation = True
        self.correct_btn.disabled = True
        self.incorrect_btn.disabled = True
        file_name = os.path.join(self.topic_path, 'correct_kw.pkl')
        with open(file_name, 'rb') as f:
            correct_kw = pickle.load(f)
        self.topic_name.text = f'Evaluation for {self.topic} completed'
        self.keyword.text = 'All keywords are evaluated'
        self.correct_answer.text = f'The number of acceptable keywords generated automatically: {str(len(correct_kw))}'
        self.total_keywords.text = f'Out of the total number of auto generated Keywords: {str(len(self.all_keywords))}'
        
        
    def display_keyword(self):
        self.topic_name.text = f'Topic being Evaluated: {self.topic}'
        if self.srno < len(self.updated_unchecked):

            self.keyword.text = self.updated_unchecked[self.srno]
        else:
            if 'checked_kw.pkl' in self.files:
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    correct_kw = pickle.load(f)
                os.remove(file_name)
                file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
                os.remove(file_name)
                new_file = os.path.join(self.topic_path, 'correct_kw.pkl')
                with open(new_file, 'wb') as f:
                    pickle.dump(correct_kw, f)
                self.evaluation_result()
            else:
                file_name = os.path.join(self.topic_path, 'correct_kw.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.correct_kw, f)
                self.evaluation_result()
            
            
    def corrected_keywords(self, instance):
        if self.is_evaluation:
            instance.disabled = True
        else:
            instance.disabled = False
        if self.srno < len(self.updated_unchecked):
            correct_kw = self.updated_unchecked[self.srno]
            self.updated_unchecked.remove(correct_kw)
            self.correct_kw.append(correct_kw)
            self.srno += 1
        else:
            print('done')
            if not len(self.updated_unchecked) > 0:
            # delete unchecked_kw.pkl
                file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
                os.remove(file_name)
                # rename checked_kw.pkl as correct_kw.pkl
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    checked_kw = pickle.load(f)
                checked_kw.extend(self.correct_kw)
                new_file = os.path.join(self.topic_path, 'correct_kw.pkl')
                with open(new_file, 'wb') as f:
                    pickle.dump(checked_kw, f)
                os.remove(file_name)
                # save and update file
        self.display_keyword()
            
        
    def incorrect_kw(self, instance):
        if self.is_evaluation:
            instance.disabled = True
        else:
            instance.disabled = False
        in_correct_kw = self.updated_unchecked[self.srno]
        self.updated_unchecked.remove(in_correct_kw)
        if self.srno < len(self.updated_unchecked):
            self.srno += 1
        elif not len(self.updated_unchecked) > 0:
            print('Done')
            if not len(self.updated_unchecked) > 0:
            # delete unchecked_kw.pkl
                file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
                os.remove(file_name)
                # rename checked_kw.pkl as correct_kw.pkl
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    checked_kw = pickle.load(f)
                checked_kw.extend(self.correct_kw)
                new_file = os.path.join(self.topic_path, 'correct_kw.pkl')
                with open(new_file, 'wb') as f:
                    pickle.dump(checked_kw, f)
                os.remove(file_name)
                # save and update file
        self.display_keyword()
        
        
    def exit_program(self):
        if not self.is_evaluation:
            file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(self.updated_unchecked, f)
            if 'checked_kw.pkl' not in self.files:
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.correct_kw, f)
            else:
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    already_checked = pickle.load(f)
                    already_checked.extend(self.correct_kw)
                with open(file_name, 'wb') as f:
                    pickle.dump(already_checked, f)
            App.get_running_app().stop()
        else:
            App.get_running_app().stop()
            
    
    def back(self):
        if not self.is_evaluation:
            file_name = os.path.join(self.topic_path, 'unchecked_kw.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(self.updated_unchecked, f)
            if 'checked_kw.pkl' not in self.files:
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.correct_kw, f)
            else:
                file_name = os.path.join(self.topic_path, 'checked_kw.pkl')
                with open(file_name, 'rb') as f:
                    already_checked = pickle.load(f)
                    already_checked.extend(self.correct_kw)
                with open(file_name, 'wb') as f:
                    pickle.dump(already_checked, f)
            sm.current = 'teacher_topic'
        else: 
            sm.current = 'teacher_topic'














class DispQuestions(Screen):
    def __init__(self, topic, **kwargs):
        super(DispQuestions, self).__init__(**kwargs)
        self.topic = topic
        self.disp_counter = 0
        topic_label = ObjectProperty(None)
        questions_label = ObjectProperty(None)
        self.update_screen()


    def update_screen(self):
        self.topic_label.text = f"The following questions were generated for: {self.topic}"
        ques_path = os.path.join(topic_path, self.topic)
        file_name = os.path.join(ques_path, 'questions.pkl')
        with open(file_name, 'rb') as f:
            questions_per_parra = pickle.load(f)
        all_questions = []
        for kw_ques_list in questions_per_parra:
            for kw, q in kw_ques_list:
                all_questions.append(q)

        for srno, ques in enumerate(all_questions):
            self.questions_label.text += f'Ques. No. {srno+1}: ' + ques + '\n\n'



    def exit_program(self):
        print("Exiting application.. ciao")
        App.get_running_app().stop()

    def disp_main_screen(self):
        sm.current = 'teacher'

    def back(self):
        sm.current = 'teacher_topic'
