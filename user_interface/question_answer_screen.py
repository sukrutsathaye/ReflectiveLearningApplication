"""
ReflectiveLearning Application
Student Arbeit Universität Siegen
@author: Sukrut S. Sathaye

User Interface: Question Answer Screen
"""

import os
import kivy
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from user_interface.global_variables import *
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.app import App
import pickle
import random
from source_code.ReflectiveLearningV7 import QuestionAnswerGenerator
from source_code.ReflectiveLearningV7 import SubQuesChecker as sqc


file_path = os.path.join(design_path, 'question_answer_screen.kv')
Builder.load_file(file_path)


class QuestionAnswerScreen(Screen):
    def __init__(self, topic, n_of_ques,chap_read, **kwargs):
        super(QuestionAnswerScreen, self).__init__(**kwargs)
        # create Rl Backend object for accessing Backend Methods
        # rl = ReflectiveLearningBackend(topic)
        self.Qno = 0
        self.questions_to_ask = 0
        self.randomize_q = 0
        # generate ObjectProperty
        status   = ObjectProperty(None)
        question = ObjectProperty(None)
        option1  = ObjectProperty(None)
        option2  = ObjectProperty(None)
        option3  = ObjectProperty(None)
        option4  = ObjectProperty(None)
        self.topic = topic
        self.cq = []
        self.questions_to_ask = n_of_ques
        self.chapters_read = chap_read
        self.is_correct_kw = False
        self.is_ques = False
        self.is_optn = False
        self.correct_count = 0
        self.questions_answered_wrong = []
        self.topic_path = os.path.join(topic_path, self.topic)
        self.files = os.listdir(self.topic_path)
        if 'correct_kw.pkl' not in self.files:
            if 'questions.pkl' in self.files:
                self.is_ques = True
                file_name = os.path.join(self.topic_path, 'questions.pkl')
                with open(file_name, 'rb') as f:
                    self.questions_per_parra = pickle.load(f)
            else:
                # print("Generate and save questions")
                qag = QuestionAnswerGenerator(topic=topic)
                self.is_ques = True
                self.questions_per_parra = qag.generate_blank_questions()
                file_name = os.path.join(self.topic_path, 'questions.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.questions_per_parra, f)
            if 'options.pkl' in self.files:
                self.is_optn = True
                file_name = os.path.join(self.topic_path, 'options.pkl')
                with open(file_name, 'rb') as f:
                    self.options = pickle.load(f)
            else:
                # print("Generate and save options")
                self.options = qag.generate_mcq_options()
                self.is_optn = True
                file_name = os.path.join(self.topic_path, 'options.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.options, f)
            if self.is_ques and self.is_optn:
                self.display_q_and_ans()
        else:
            self.is_correct_kw = True
            file_name = os.path.join(self.topic_path, 'correct_kw.pkl')
            with open(file_name, 'rb') as f:
                correct_kw = pickle.load(f)
            file_name = os.path.join(self.topic_path, 'questions.pkl')
            with open(file_name, 'rb') as f:
                self.questions_per_parra = pickle.load(f)
            file_name = os.path.join(self.topic_path, 'options.pkl')
            with open(file_name, 'rb') as f:
                self.options = pickle.load(f)
            self.approved_questions = [None]*len(self.questions_per_parra)
            for srno, q in enumerate(self.approved_questions):
                self.approved_questions[srno] = []
            a_kw_q = []
            all_questions = self.get_all_questions(self.questions_per_parra)
            for kw in correct_kw:
                for kw_q in all_questions:
                    if kw == kw_q[0]:
                        a_kw_q.append(kw_q)
            # print("Approved Questions",a_kw_q)
            for srno, kw_q_parra in enumerate(self.questions_per_parra):
                for approved_ques in a_kw_q:
                    if approved_ques in kw_q_parra:
                        self.approved_questions[srno].append(approved_ques) 
            self.display_q_and_ans()
            

    def display_q_and_ans(self):

        # print("Here", self.chapters_read)
        if self.chapters_read == 0:
            
            if self.is_correct_kw:
                questions = self.approved_questions[0]
            else:
                questions = self.questions_per_parra[0]
            # print("Questions: ", questions)
        else:
            # print("Chapters read:", self.chapters_read)
            if self.is_correct_kw:
                questions = self.approved_questions[:self.chapters_read + 1]
                # print("Questions: ", questions)
            else:
                questions = self.questions_per_parra[:self.chapters_read + 1]
        self.all_questions = self.get_all_questions(questions)
        # print("All questions: ",len(self.all_questions))
        self.randomize_q = random.sample(range(0, len(self.all_questions)),
            int(self.questions_to_ask))
        # print(self.randomize_q)
        self.ask_one_question()


    def ask_one_question(self):
        if self.Qno < int(self.questions_to_ask):
            kw, self.q = self.all_questions[self.randomize_q[self.Qno]]
            # kw, self.q = self.all_questions[0]
            # print("First Question:",self.all_questions[0])
            self.question.text = f'Question No. {self.Qno + 1}:  ' + self.q
            options = self.options[kw]
            self.correct_optn = options[0]
            # print("Options: ", options)
            randomize_optn = random.sample(range(0, len(options)), 4)
            # print(randomize_optn)
            self.option1.text = options[randomize_optn[0]]
            self.option2.text = options[randomize_optn[1]]
            self.option3.text = options[randomize_optn[2]]
            self.option4.text = options[randomize_optn[3]]
        else:
            print("show Pop Up")
            # print("wrong Ques: ",self.questions_answered_wrong)
            show = AnalysisPopUp(c_count=self.correct_count, topic=self.topic,
                w=self.questions_answered_wrong, 
                total_ques=self.questions_to_ask, cq=self.cq)
            global popupWindow
            popupWindow = Popup(title ="Analysis?", content = show,
                            size_hint =(None, None), size =(400, 400))
            popupWindow.open()



    def option_selected(self, instance):
        if instance.text == self.correct_optn:
            self.status.text = 'Correct Answer, well done!'
            self.correct_count += 1
            self.cq.append(self.q)
            # print("Here now")
            # print(self.cq)
        else:
            self.status.text = f'Wrong Answer, correct Answer is: {self.correct_optn}'
            self.questions_answered_wrong.append((self.q, self.correct_optn))
        self.Qno += 1
        self.ask_one_question()
        # time.sleep(3)

    def get_all_questions(self, questions):
        all_questions = []
        for kw_q_in_list in questions:
            for kw_q in kw_q_in_list:
                all_questions.append(kw_q)
        return all_questions


class AnalysisPopUp(GridLayout):
    def __init__(self, c_count, w, total_ques, topic, cq, **kwargs):
        super(AnalysisPopUp, self).__init__(**kwargs)
        self.c_count = c_count
        self.w = w
        self.total_ques = total_ques
        self.topic = topic
        self.cq = cq
        # print("From popup", self.cq)

    def yes_or_no(self, instance):
        if instance.text == 'yes':
            print("Total Questions: ", self.total_ques)
            analysis_screen = AnalysisScreen(name='analysis', topic=self.topic,
                c_count=self.c_count, total_ques=self.total_ques,
                w=self.w, cq=self.cq)
            global popupWindow
            popupWindow.dismiss()
            sm.add_widget(analysis_screen)
            sm.current = 'analysis'
        else:
            App.get_running_app().stop()


class AnalysisScreen(Screen):
    def __init__(self, topic, c_count, w, total_ques, cq,**kwargs):
        super(AnalysisScreen, self).__init__(**kwargs)
        marks = ObjectProperty(None)
        wrong_questions = ObjectProperty(None)
        self.score_input = str(c_count) + '/' + str(total_ques)
        print("Score: ", self.score_input)
        self.w_ques = w
        self.cq = cq
        self.update_analysis_screen()
        
        # print("Correct Q:", self.cq)
        
    
    def update_analysis_screen(self):
        self.marks.text = f'Your Score is: {self.score_input}'
        wrong_q_text = ''
        for qno, quest in enumerate(self.w_ques):
            wrong_q_text += f'Ques. No. {qno + 1}:  ' + quest[0] + f'\n====>  Correct Option is: {quest[1]}\n'
        wrong_q_text += '\n\n'
        wrong_q_text += 'The following Questions were answered correctly!\n\n'
        for qno, ques in enumerate(self.cq):
            wrong_q_text += f'Ques. No. {qno + 1}:  ' + ques + '\n'
        self.wrong_questions.text = wrong_q_text
            
        
    def continue_learning(self):
        sm.current = 'student'
        
    
    def exit(self):
        App.get_running_app().stop()
        
    
class SubjectiveQuestionScreen(Screen):
    def __init__(self, topic,**kwargs):
        super(SubjectiveQuestionScreen, self).__init__(**kwargs)
        # object properties to access in .kv file
        question = ObjectProperty(None)
        answer = ObjectProperty(None)
        status = ObjectProperty(None)
        # initialise other parameters
        is_ques = False
        is_ans = False
        self.data = []
        self.topic = topic
        self.q_no = 0
        self.checker = sqc()
        self.topic_path = os.path.join(topic_path, self.topic)
        self.files = os.listdir(self.topic_path)
        if 'csubj_questions.pkl' not in self.files:
            if 'subj_questions.pkl' in self.files:
                is_ques = True
                file_name = os.path.join(self.topic_path, 'subj_questions.pkl')
                with open(file_name, 'rb') as f:
                    self.subj_questions = pickle.load(f)
            if 'subj_answers.pkl' in self.files:
                is_ans = True
                file_name = os.path.join(self.topic_path, 'subj_answers.pkl')
                with open(file_name, 'rb') as f:
                    self.subj_answers = pickle.load(f)
            if not is_ques and not is_ans:
                self.subj_questions, self.subj_answers = self.rl.qag.get_all_subjective_questions_answers()
                is_ques = True
                is_ans = True
                # save the generated variables
                file_name = os.path.join(self.topic_path, 'subj_questions.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.subj_questions, f)
                file_name = os.path.join(self.topic_path, 'subj_answers.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.subj_answers, f)
            # display screen
            if is_ques and is_ans:
                self.update_screen()
        else:
            file_name = os.path.join(self.topic_path, 'csubj_questions.pkl')
            with open(file_name, 'rb') as f:
                self.subj_questions = pickle.load(f)
            file_name = os.path.join(self.topic_path, 'subj_answers.pkl')
            with open(file_name, 'rb') as f:
                self.subj_answers = pickle.load(f)
            self.update_screen()
    
    
    def update_screen(self):
        if self.q_no < len(self.subj_questions):
            self.kw, q = self.subj_questions[self.q_no]
            try:
                model_answer_list = self.subj_answers[self.kw]
            except KeyError:
                model_answer_list = []
            if not len(model_answer_list) == 0:
                if self.q_no < len(self.subj_questions):
                    # print("All subjective questions: ", self.subj_questions)
                    self.kw, q = self.subj_questions[self.q_no]
                    self.question.text = q
                    self.answer.text = ''
                else:
                    dqas = DefQuesAnalysisScreen(name='dqas',
                            topic=self.topic, data=self.data)
                    sm.add_widget(dqas)
                    sm.current = 'dqas'
            else:
                self.q_no += 1
                self.update_screen()
        else:
            dqas = DefQuesAnalysisScreen(name='dqas',
                            topic=self.topic, data=self.data)
            sm.add_widget(dqas)
            sm.current = 'dqas'


    def check_answer(self):
        # need to improve a bit
        # print("Check Answer using cosine similarity")
        user_given_ans = self.answer.text
        try:
            model_answer_list = self.subj_answers[self.kw]
            # print("Source ans: ", model_answer_list)
            model_answer = ''
            for ans in model_answer_list:
                model_answer += ans
        except KeyError:
            model_answer = ''
        sim = self.checker.compare_2_sentences(model_answer, user_given_ans)
        # print("Model Ans: ", model_answer)
        # print("User Ans: ", user_given_ans)
        # print("Similarity is: ", sim)
        
        if sim >= 0.75:
            self.status.text = 'Correct Answer.'
        elif 0.4 <= sim < 0.75:
            self.status.text = 'Answer may be correct.'
        elif 0.2 <= sim < 0.4:
            self.status.text = 'Answer may be wrong.'
        else:
            self.status.text = 'Wrong Answer.'
        data = (self.question.text, model_answer, 
                user_given_ans, sim, self.status.text)
        self.data.append(data)
        self.q_no += 1
        self.update_screen()
        
        
class DefQuesAnalysisScreen(Screen):
    def __init__(self, topic, data,**kwargs):
        super(DefQuesAnalysisScreen, self).__init__(**kwargs)
        self.topic = topic
        self.data = data
        # Set Object Properties: 
        topic_name = ObjectProperty(None)
        display = ObjectProperty(None)
        self.update_screen()
        
            
    def update_screen(self):
        self.topic_name.text = f'Topic: {self.topic}'
        self.display.text = ''
        for data_tuple in self.data:
            for srno, data_element in enumerate(data_tuple):
                if srno == 0:
                    self.display.text += 'Question:  ' + data_element + '\n'
                elif srno == 1:
                    self.display.text += 'Predicted Definition:  ' + data_element + '\n'
                elif srno == 2:
                    self.display.text += 'Your Answer:  ' + data_element + '\n'
                elif srno == 3:
                    self.display.text += 'Similarity Score:  ' + str(data_element) + '\n'
                elif srno == 4:
                    self.display.text += 'Predicted Result:  ' + data_element + '\n'
            self.display.text += '\n\n'
            
                
                
    def continue_learning(self):
        sm.current = 'student'
        
        
    def quit_program(self):
        App.get_running_app().stop()
                