"""
This application aims at auto generating questions and answers
to help the user learn reflectively.

@author: sukrut
*** Reflective Learning App V7 ***
*** Universität Siegen ***

"""
import re
import wikipedia as wiki
from bs4 import BeautifulSoup as bs
import requests
import spacy
import gensim
from rake_nltk import Rake
from sklearn.feature_extraction.text import TfidfVectorizer
import textacy
import textacy.ke
import time
import pandas as pd
import gensim.downloader as api
import numpy as np
import random
import pickle
import os
from nltk.corpus import words as nltk_words
import inflect
from english_words import english_words_set
import spacy_universal_sentence_encoder as sent_encoder
from source_code.OptionGenerator import PowerTheasurus as pt
from user_interface.global_variables import topic_path
import pprint





class ScrapeText:
    """
    This class is responsible for getting the text from
    the web, especially wikipedia.
    """


    def __init__(self, topic=None):
        if topic is None:
            self.topic = "Black Hole"
        else:
            self.topic = topic
        self.source = self.convert_topic_to_source(self.topic)


    def convert_topic_to_source(self, topic):
        """
        This function converts any topic into its equivalent
        http source link, which could be used to extract text from web.

        Parameters
        ----------
        topic : str
            A topic in string format is excepted which the user wants
            to learn from.

        Returns
        -------
        source : str
            A http string which can be directly used to extract
            text from wikipedia.

        """
        topic_wrds = topic.split()
        source = "https://en.wikipedia.org/wiki/"
        source_kw = ''
        for word in topic_wrds:
            source_kw += word.lower() + '_'
        source_kw = source_kw[:-1]
        source += source_kw
        return source


    def get_raw_text(self):
        """
        This function is used to grab raw text from wikipedia
        depending on the topic passed in through constructor of
        any instance of this class

        Returns
        -------
        raw_text : str
            Entire text extracted from the wikipedia link.
            The text is obviously raw and unprocessed.
        paras : list
            list containing the raw text as it appears in the
            paragraphs throughout the article.
        heads: list
            list of headings for each paragraphs of the text
            scraped from the internet

        """
        html_text = requests.get(url=self.source)
        soup = bs(html_text.text, 'html.parser')

        # Extract the plain text content from paragraphs
        paras = []
        for paragraph in soup.find_all('p'):
            # print("P: ", paragraph, type(paragraph))

            paras.append(str(paragraph.text))

        # Extract text from paragraph headers
        heads = []
        for head in soup.find_all('span', attrs={'mw-headline'}):
            heads.append(str(head.text))

        # Interleave paragraphs & headers
        text = [val for pair in zip(paras, heads) for val in pair]
        raw_text = ' '.join(text)
        return raw_text, paras, heads


class ProcessText(ScrapeText):


    def __init__(self, topic=None):
        super().__init__(topic)
        self.path = os.path.join(topic_path, topic)
        try:
            self.nlp = spacy.load('en_core_web_lg')
        except Exception:
            print("Please download spacy language model and try again")
        # print(self.path)
        self.stopwords = [
            "a", "about", "above", "after", "again", "against",
            "all", "am", "an", "and", "any", "are", "as", "at", "be",
            "because", "been", "before", "being", "below","between", "both",
            "but", "by", "could", "did", "do", "does", "doing", "down",
            "during", "each", "few", "for", "from", "further", "had",
            "has", "have", "having", "he", "he'd", "he'll", "he's", "her",
            "here", "here's", "hers", "herself", "him", "himself","his",
            "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in",
            "into", "is", "it", "it's", "its", "itself", "let's", "me",
            "more", "most", "my", "myself","nor", "of", "on", "once",
            "only", "or", "other", "ought", "our", "ours", "ourselves",
            "out", "over", "own", "same", "she", "she'd", "she'll", "she's",
            "should", "so", "some", "such", "than", "that", "that's", "the",
            "their", "theirs", "them", "themselves", "then", "there",
            "there's", "these", "they", "they'd", "they'll", "they're",
            "they've", "this", "those", "through", "to", "too", "under",
            "until","up", "very", "was", "we", "we'd", "we'll", "we're",
            "we've", "were", "what", "what's", "when", "when's", "where",
            "where's", "which", "while", "who", "who's", "whom", "why",
            "why's", "with", "would", "you", "you'd", "you'll", "you're",
            "you've", "your", "yours", "yourself", "yourselves"]

        self.inflect = inflect.engine()
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        self.irregular = {'man'   : 'men',
                          'child' : 'children',
                          'foot'  : 'feet',
                          'tooth' : 'teeth',
                          'mouse' : 'mice',
                          'person': 'people'}
        self.no_change = ['sheep', 'deer', 'fish', 'series', 'species']
        self.f_exeptions = ['roof', 'cliff','roofs', 'cliffs']

        self.raw_text, self.paragraphs, self.heads = self.get_raw_text()

        for srno, para in enumerate(self.paragraphs):
            if len(para) < 70:
                self.paragraphs.pop(srno)
        self.text_per_para = [None]*len(self.paragraphs)
        for srno, para in enumerate(self.paragraphs):
            self.text_per_para[srno] = para.split()

        # Call some default functions from Constructor
        print("Checkpoint Reached!!!")
        self.make_dir_for_topic()
        self.clean_text()


    def remove_punctuations(self, debug=False):


        for text_list in self.text_per_para:
            for srno, word in enumerate(text_list):
                if ',' in word:
                    new_word = word.split(sep=',')
                    text_list[srno] = new_word[0]
                    if debug:
                        print(word, new_word, new_word[1])
                elif '"' in word:
                    new_word = word.split(sep='"')
                    text_list[srno] = new_word[1]
                    if debug:
                        print(word, new_word, new_word[1])
                elif '(' in word:
                    new_word = word.split(sep='(')
                    text_list[srno] = new_word[1]
                    if debug:
                        print(word, new_word, new_word[1])
                elif ')' in word:
                    new_word = word.split(sep=')')
                    text_list[srno] = new_word[0]
                    if debug:
                        print(word, new_word, new_word[0])
                elif '[' in word:
                    new_word = word.split(sep='[')
                    text_list[srno] = new_word[0]
                    if debug:
                        print(word, new_word, new_word[0])
                elif ']' in word:
                    new_word = word.split(sep=']')
                    text_list[srno] = new_word[0]
                    if debug:
                        print(word, new_word, new_word[0])
                elif '{' in word:
                    new_word = word.split(sep='{')
                    text_list[srno] = new_word[0]
                    if debug:
                        print(word, new_word, new_word[0])

        for srno, para in enumerate(self.text_per_para):
            self.text_per_para[srno] = " ".join(para)

        for text in self.text_per_para:
            text = re.sub(r"\[\d]", "", text)
            text = re.sub(r"\[\d\d]", "", text)
            text = re.sub(r"\[\d\d\d]", "", text)
            text = re.sub(r"\[\w\w\w\w\w\w]", "", text)
        text_per_para = self.text_per_para
        return text_per_para


    def normalize_case(self):
        for para in self.text_per_para:
            for words in para:
                words = words.lower()
        text_per_para = self.text_per_para
        return text_per_para


    def clean_text(self, save_data=True):
        is_file = False
        path = self.folder_path
        files = os.listdir(path)
        for file in files:
            if file == 'text.pkl':
                is_file = True
                file_name = os.path.join(path, file)
                with open(file_name, 'rb') as f:
                    self.text_per_para = pickle.load(f)
        self.paras_in_str = self.text_per_para
        if not is_file:
            self.remove_punctuations()
            self.normalize_case()
            # self.remove_punctuations()
            for srno, text_in_parra in enumerate(self.text_per_para):
                if len(text_in_parra) <= 20:
                    self.text_per_para.pop(srno)
            self.paras_in_str = self.text_per_para
            if save_data:
                file_name = os.path.join(self.folder_path, 'text.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(self.text_per_para, f)
        return self.text_per_para


    def make_dir_for_topic(self):
        # self.path = os.path.join(self.path, "Topics")
        # try:
        #     os.mkdir(self.path)
        # except OSError:
        #     pass
        self.folder_path = self.path

        # see if topic folder already exists:
        stored_topics = os.listdir(topic_path)
        if self.topic not in stored_topics:
            try:
                os.mkdir(self.folder_path)
            except OSError as e:
                print(e)
        self.folder_names = {self.topic:self.folder_path}


    def process_with_spacy(self):
        doc = [None]*len(self.paragraphs)
        for srno, para in enumerate(self.text_per_para):
            doc[srno] = self.nlp(para)
        self.doc = doc
        return doc


    def process_with_textacy(self):
        en = textacy.load_spacy_lang('en_core_web_lg')
        # en.add_pipe(en.create_pipe('sentencizer'))
        self.texacy_doc = [None]*len(self.paragraphs)
        for srno, para in enumerate(self.paras_in_str):
            self.texacy_doc[srno] = textacy.make_spacy_doc(para, lang=en)


    def plural_to_singular(self, plurals):
        if type(plurals) == str:
            is_single = True
        elif type(plurals) == list:
            is_single = False
        if is_single:
            if plurals not in list(self.irregular.values()) + self.no_change:
                last_letter = plurals[-1]
                s_last_letter = plurals[-2]
                t_last_letter = plurals[-3]
                if last_letter == 's':
                    if plurals not in self.f_exeptions:
                        if s_last_letter == 'e' and t_last_letter not in ['v', 'i']:
                            sing_word = plurals[:-2]
                        elif s_last_letter == 'e' and t_last_letter == 'i':
                            sing_word = plurals[:-3] + 'y'
                        elif s_last_letter == 'e' and t_last_letter == 'v':
                            sing_word = plurals[:-3] + 'f'
                            if not sing_word in nltk_words.words():
                                sing_word += 'e'
                        elif s_last_letter != 'e':
                            sing_word = plurals[:-1]
                        elif s_last_letter == 'e' and t_last_letter == 'l':
                            sing_word = plurals[:-1]
                    else:
                        sing_word = plurals[:-1]
            elif plurals in list(self.irregular.values()):
                for sing, plu in self.irregular.items():
                    if plurals == plu:
                        sing_word = sing
            elif plurals in self.no_change:
                sing_word = plurals
            return sing_word
        else:
            singular = []
            for word in plurals:
                assert type(word) == str
                if word not in list(self.irregular.values()) + self.no_change:
                    last_letter = word[-1]
                    s_last_letter = word[-2]
                    t_last_letter = word[-3]
                    if last_letter == 's':
                        if word not in self.f_exeptions:
                            if s_last_letter == 'e' and t_last_letter not in ['v', 'i']:
                                sing_word = word[:-2]
                                singular.append(sing_word)
                            elif s_last_letter == 'e' and t_last_letter == 'i':
                                sing_word = word[:-3] + 'y'
                                singular.append(sing_word)
                            elif s_last_letter == 'e' and t_last_letter == 'v':
                                sing_word = word[:-3] + 'f'
                                if not sing_word in nltk_words.words():
                                    sing_word += 'e'
                                    singular.append(sing_word)
                                else:
                                    singular.append(sing_word)
                            elif s_last_letter != 'e':
                                sing_word = word[:-1]
                                singular.append(sing_word)
                        else:
                            singular.append(word[:-1])
                elif word in list(self.irregular.values()):
                    for sing, plu in self.irregular.items():
                        if word == plu:
                            singular.append(sing)
                elif word in self.no_change:
                    singular.append(word)
            return singular


    def singular_to_plural(self, singular):
        if type(singular) == str:
            is_single = True
        elif type(singular) == list:
            is_single = False
        if is_single:
            if singular not in list(self.irregular.keys()) + self.no_change:
                last_letter = singular[-1]
                s_last_letter = singular[-2]
                if last_letter in ['s','x','z']:
                    plu_word = singular + 'es'
                elif last_letter == 'h' and s_last_letter in ['c', 's']:
                    plu_word = singular + 'es'
                elif last_letter == 'f':
                    if singular in self.f_exeptions:
                        plu_word = singular + 's'
                    else:
                        plu_word = singular[:-1] + 'ves'
                elif s_last_letter == 'f' and last_letter == 'e':
                    plu_word = singular[:-2] + 'ves'
                elif s_last_letter in self.vowels and last_letter == 'y':
                    plu_word = singular + 's'
                elif s_last_letter not in self.vowels and last_letter == 'y':
                    plu_word = singular[:-1] + 'ies'
                elif s_last_letter in self.vowels and last_letter == 'o':
                    plu_word = singular + 's'
                elif s_last_letter not in self.vowels and last_letter == 'o':
                    plu_word = singular + 'es'
                else:
                    plu_word = singular + 's'
            elif singular in self.no_change:
                plu_word = singular
            elif singular in list(self.irregular.keys()):
                plu_word = self.irregular[singular]
            return plu_word
        else:
            plurals = []
            for word in singular:
                assert type(word) == str
                if word not in list(self.irregular.keys()) + self.no_change:
                    last_letter = word[-1]
                    second_last_letter = word[-2]
                    if last_letter in ['s','x','z']:
                        plu_word = word + 'es'
                        plurals.append(plu_word)
                    elif last_letter == 'h' and second_last_letter in ['c', 's']:
                        plu_word = word + 'es'
                        plurals.append(plu_word)
                    elif last_letter == 'f':
                        if word in self.f_exeptions:
                            plu_word = word + 's'
                            plurals.append(plu_word)
                        else:
                            plu_word = word[:-1] + 'ves'
                            plurals.append(plu_word)
                    elif second_last_letter == 'f' and last_letter == 'e':
                        plu_word = word[:-2] + 'ves'
                        plurals.append(plu_word)
                    elif second_last_letter in self.vowels and last_letter == 'y':
                        plu_word = word + 's'
                        plurals.append(plu_word)
                    elif second_last_letter not in self.vowels and last_letter == 'y':
                        plu_word = word[:-1] + 'ies'
                        plurals.append(plu_word)
                    elif second_last_letter in self.vowels and last_letter == 'o':
                        plu_word = word + 's'
                        plurals.append(plu_word)
                    elif second_last_letter not in self.vowels and last_letter == 'o':
                        plu_word = word + 'es'
                        plurals.append(plu_word)
                    else:
                        plu_word = word + 's'
                        plurals.append(plu_word)
                elif word in self.no_change:
                    plu_word = word
                    plurals.append(plu_word)
                elif word in list(self.irregular.keys()):
                    plurals.append(self.irregular[word])
            return plurals


    def sentences_per_parra(self):
        sents_per_parra = [None]*len(self.text_per_para)
        for srno, text in enumerate(self.text_per_para):
            sentences = text.split('.')
            # sents_per_parra[srno] = sentences
            new_sents = []
            for sents in sentences:
                if len(sents) > 15:
                    n_sents = sents + '.'
                    new_sents.append(n_sents)
            sents_per_parra[srno] = new_sents
        return sents_per_parra


class ExtractKeyWords(ProcessText):


    def __init__(self, topic=None):
        super().__init__(topic)
        self.kw = textacy.ke
        self.r = Rake(stopwords=self.stopwords,language='english')
        self.process_with_spacy()
        self.process_with_textacy()


    def kw_textrank(self, no_of_kwords=None):
        if no_of_kwords is None:
            no_of_kwords = 5
        keywrds_per_para = [None]*len(self.texacy_doc)
        for srno, doc in enumerate(self.texacy_doc):
            keywrds_per_para[srno] = self.kw.textrank(
                doc,window_size=100,topn=no_of_kwords,normalize='lower')
        return keywrds_per_para


    def kw_sgrank(self, thres=None):
        if thres is None:
            thres = 0.3
        keywrds_per_para = [None]*len(self.texacy_doc)
        for srno, doc in enumerate(self.texacy_doc):
            try:
                keywrds_per_para[srno] = self.kw.sgrank(doc,
                    ngrams=(1,2),window_size=100,topn=0.1,normalize='lower')
            except TypeError:
                pass
        return keywrds_per_para


    def kw_scake(self, topn=None):
        if topn is None:
            topn = 5
        keywrds_per_para = [None]*len(self.texacy_doc)
        for srno, doc in enumerate(self.texacy_doc):
            keywrds_per_para[srno] = self.kw.scake(doc,topn=topn)
        return keywrds_per_para


    def kw_yake(self, topn=None):
        if topn is None:
            topn = 0.3
        keywrds_per_para = [None]*len(self.texacy_doc)
        for srno, doc in enumerate(self.texacy_doc):
            try:
                keywrds_per_para[srno] = self.kw.yake(doc,ngrams=(2),
                    window_size=100,topn=topn)
            except Exception:
                pass
        return keywrds_per_para


    def gen_keywrds_tf_idf(self, factor=None):
        if factor is None:
            factor = 0.70
        dataset = self.text_per_para
        tfIdfVectorizer = TfidfVectorizer(use_idf=True,ngram_range=(2),
            stop_words='english')
        tfIdf = tfIdfVectorizer.fit_transform(dataset)
        df = pd.DataFrame(tfIdf[0].T.todense(),
            index=tfIdfVectorizer.get_feature_names(), columns=["TF-IDF"])
        df = df.sort_values('TF-IDF', ascending=False)
        print (df.head(50))


    def generate_keywrds_rake(self):
        keywrds_per_para = [None]*len(self.paragraphs)
        for srno, para in enumerate(self.paras_in_str):
            self.r.extract_keywords_from_text(para)
            keywrds_per_para[srno] = self.r.get_ranked_phrases()
        self.keywrds_per_para = keywrds_per_para
        return keywrds_per_para


    def extract_kw_from_list(self, kw_list):
        kws = [None]*len(kw_list)
        for srno, kw in enumerate(kw_list):
            try:
                kw_in_para = [None]*len(kw)
                for srno1, kw1 in enumerate(kw):
                    kw_in_para[srno1] = kw1[0]
                kws[srno] = kw_in_para
            except TypeError:
                pass
        return kws


    def combined_kw_per_parra(self):
        t_kw = self.kw_textrank()
        sg_kw = self.kw_sgrank()
        y_kw = self.kw_yake()
        sc_kw = self.kw_scake()
        kw1 = self.extract_kw_from_list(t_kw)
        kw2 = self.extract_kw_from_list(sg_kw)
        kw3 = self.extract_kw_from_list(y_kw)
        kw4 = self.extract_kw_from_list(sc_kw)
        combined_keywords = [None]*len(self.paragraphs)
        for p in range(0, len(self.paragraphs)):
            if kw1[p] == None:
                comb_list = kw2[p] + kw3[p] + kw4[p]
            elif kw2[p] == None:
                comb_list = kw1[p] + kw3[p] + kw4[p]
            elif kw3[p] == None:
                comb_list = kw1[p] + kw2[p] + kw4[p]
            elif kw4[p] == None:
                comb_list = kw1[p] + kw2[p] + kw3[p]
            elif kw1[p] != None and kw2[p] != None and kw3[p] != None and kw4[p] != None:
                comb_list = kw1[p] + kw2[p] + kw3[p] + kw4[p]

            combined_keywords[p] = (list(set(comb_list)))
        # perform primary cleaning
        # final_keywords = [None]*len(self.paragraphs)
        # for srno, kw in enumerate(final_keywords):
        #     final_keywords[srno] = []
        # for srno, kw_list in enumerate(combined_keywords):
        #     for kw in kw_list:
        #         words = kw.split()
        #         if len(words) == 1:
        #             if len(words[0]) >= 3 and words[0].isalpha():
        #                 final_keywords[srno].append(kw.lower())
        #         elif len(words) >= 2:
        #             kw_new = ''
        #             for s, word in enumerate(words):
        #                 if len(word) >= 3 and word.isalpha():
        #                     kw_new += word.lower() + ' '
        #             kw_new = kw_new[:-1]
        #             if kw_new != '':
        #                 final_keywords[srno].append(kw_new)
        return combined_keywords


    def get_pos_of_all_keywords(self, kw_list=None):
        if kw_list is None:
            kw_per_parra = self.combined_kw_per_parra()
            is_single_list = False
        else:
            is_single_list = True
        keywrd_pos = {}
        if not is_single_list:
            for kw_in_parra in kw_per_parra:
                for kw in kw_in_parra:
                    words = kw.split()
                    doc = []
                    pos = []
                    for word in words:
                        doc.append(self.nlp(word))
                    for d in doc:
                        for token in d:
                            pos.append(token.pos_)
                    keywrd_pos[kw] = pos
            return keywrd_pos
        else:
            for kw in kw_list:
                words = kw.split()
                doc = []
                pos = []
                for word in words:
                    doc.append(self.nlp(word))
                for d in doc:
                    for token in d:
                        pos.append(token.pos_)
                keywrd_pos[kw] = pos
            return keywrd_pos


    def filter_keywords_using_pos(self):
        is_file = False
        path = self.folder_path
        files = os.listdir(path)
        if 'keywords.pkl' in files:
            is_file = True
            file_name = os.path.join(path, 'keywords.pkl')
            with open(file_name, 'rb') as f:
                kw_per_parra = pickle.load(f)
        if 'people_names.pkl' in files:
            file_name = os.path.join(path, 'people_names.pkl')
            with open(file_name, 'rb') as f:
                self.people_names = pickle.load(f)
        if 'similar_words.pkl' in files:
            file_name = os.path.join(path, 'similar_words.pkl')
            with open(file_name, 'rb') as f:
                self.nouns = pickle.load(f)
        if not is_file:
            keyword_pos = self.get_pos_of_all_keywords()
            all_keywords = list(keyword_pos.keys())
            self.people_names = []
            self.nouns = []
            filtered_keywords = []
            for kw, pos_list in keyword_pos.items():
                if len(pos_list) == 1:
                    # print(kw)
                    if pos_list[0] == 'NOUN' and len(kw) >= 4:
                        filtered_keywords.append(kw)
                    elif pos_list[0] == 'PROPN':
                        if kw in english_words_set:
                            filtered_keywords.append(kw)
                elif len(pos_list) == 2:
                    if pos_list[0] == 'PROPN' and pos_list[1] == 'PROPN':
                        self.people_names.append(kw)
                        filtered_keywords.append(kw)
                    elif pos_list[0] == 'ADJ' and pos_list[1] in ['NOUN', 'PROPN']:
                        filtered_keywords.append(kw)
                elif len(pos_list) == 3:
                    if pos_list[0] == 'ADJ' and pos_list[1] == 'ADJ' and pos_list[2] in ['NOUN', 'PROPN']:
                        filtered_keywords.append(kw)
                    elif pos_list[0] == 'PROPN' and pos_list[1] == 'PROPN' and pos_list[2] == 'PROPN':
                        filtered_keywords.append(kw)
                        self.people_names.append(kw)
                    elif pos_list[0] == 'ADJ' and pos_list[1] in ['NOUN', 'PROPN'] and pos_list[2] in ['NOUN', 'PROPN']:
                        filtered_keywords.append(kw)
                    elif pos_list[0] == 'ADJ' and pos_list[1] in ['NOUN', 'PROPN'] and pos_list[2] == 'VERB':
                        filtered_keywords.append(kw)
                elif len(pos_list) == 4:
                    if pos_list[0] == 'PROPN' and pos_list[1] == 'PROPN' and pos_list[2] == 'PROPN' and pos_list[3] == 'PROPN':
                        self.people_names.append(kw[2:])
                        filtered_keywords.append(kw[2:])
            for kw, pos_list in keyword_pos.items():
                if len(pos_list) >= 2:
                    words = kw.split()
                    for srno, pos in enumerate(pos_list):
                        if pos in ['NOUN', 'PROPN']:
                            try:
                                self.nouns.append(words[srno])
                            except IndexError:
                                pass
            self.similar_words = {}
            self.nouns = list(set(self.nouns))
            for noun in self.nouns:
                self.similar_words[noun] = []
                for kw in all_keywords:
                    if noun in kw:
                        self.similar_words[noun].append(kw)
            for srno, kw in enumerate(filtered_keywords):
                if kw + 's' in filtered_keywords:
                    id_s = filtered_keywords.index(kw + 's')
                    filtered_keywords.pop(id_s)
            kw_per_parra = self.combined_kw_per_parra()
            for srno, kw_list in enumerate(kw_per_parra):
                final_kw_per_parra = []
                for kw in kw_list:
                    if kw in filtered_keywords:
                        final_kw_per_parra.append(kw)
                kw_per_parra[srno] = final_kw_per_parra
            # save the files
            file_name = os.path.join(path, 'keywords.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(kw_per_parra, f)
            file_name = os.path.join(path, 'people_names.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(self.people_names, f)
            file_name = os.path.join(path, 'similar_words.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(self.similar_words, f)
        return kw_per_parra


    def get_all_keywords(self):
        cleaned_keywords = self.filter_keywords_using_pos()
        all_keywords = []
        for kw_list in cleaned_keywords:
            for kw in kw_list:
                all_keywords.append(kw)
        all_keywords = list(set(all_keywords))
        return all_keywords


    def extract_all_keywords(self, kw_list):
        all_keywords = []
        for kw_in_parra in kw_list:
            try:
                for kw in kw_in_parra:
                    all_keywords.append(kw)
            except TypeError:
                pass
        all_keywords = list(set(all_keywords))
        return all_keywords




    def compare_keywords(self, per_parra=False):
        t_kw  = self.kw_textrank()
        sg_kw = self.kw_sgrank()
        y_kw  = self.kw_yake()
        sc_kw = self.kw_scake()
        rake = self.generate_keywrds_rake()
        kw1   = self.extract_kw_from_list(t_kw)
        kw2   = self.extract_kw_from_list(sg_kw)
        kw3   = self.extract_kw_from_list(y_kw)
        kw4   = self.extract_kw_from_list(sc_kw)
        kw5   = self.extract_kw_from_list(rake)
        kw1 = self.extract_all_keywords(kw1)
        kw2 = self.extract_all_keywords(kw2)
        kw3 = self.extract_all_keywords(kw3)
        kw4 = self.extract_all_keywords(kw4)
        kw5 = self.extract_all_keywords(kw5)
        if not per_parra:
            compare_keywords = {
                'textrank' : kw1,
                'sgrank'   : kw2,
                'yake'     : kw3,
                'scake'    : kw4,
                'rake'     : rake
                }
        else:
            compare_keywords = {
                'textrank' : t_kw,
                'sgrank'   : sg_kw,
                'yake'     : y_kw,
                'scake'    : sc_kw,
                'rake'     : rake
                }
        return compare_keywords






    def evaluate_generated_keywords(self):
        all_keywords = self.get_all_keywords()
        correct_kw = []
        correct_score = 0
        total_score = len(all_keywords)
        incorrect_kw = []
        print(f"There are total of {len(all_keywords)} generated automatically")
        print("Please evaluate the following keywords generated\n")
        for kw in all_keywords:
            while True:
                print('\n',kw)
                decide = input("Enter c for correct kw and i for incorrect: ")
                if decide == 'c':
                    correct_kw.append(kw)
                    correct_score += 1
                    break
                elif decide == 'i':
                    incorrect_kw.append(kw)
                    break
                else:
                    print("Invalid input, please enter proper keys. ")
        self.correct_kw = correct_kw
        self.score = (correct_score/total_score)*100
        self.incorrect_kw = incorrect_kw
        return correct_kw, self.score, incorrect_kw


    def get_kw_freq(self):
        clean_keywords_per_parra = self.filter_keywords_using_pos()
        kw_freq = {}
        i = 0
        for kw_list in clean_keywords_per_parra:
            for kw in kw_list:
                if kw not in list(kw_freq.keys()):
                    kw_freq[kw] = f'{i}'
                elif kw in list(kw_freq.keys()):
                    i += 1
                    kw_freq[kw] = f'{i}'
        return kw_freq


    def get_top_keywords(self, set_threshold=None):
        if set_threshold is None:
            set_threshold = 10
        kw_freq = self.get_kw_freq()
        vals = list(kw_freq.values())
        keys = list(kw_freq.keys())
        int_vals = []
        i_vals = []
        for srno, val in enumerate(vals):
            int_vals.append((srno, int(val)))
            i_vals.append(int(val))
        i_vals = np.asarray(i_vals)
        max_val = np.max(i_vals)
        threshold = max_val - set_threshold
        top_kw = []
        for srno, val in enumerate(vals):
            if int(val) >= threshold:
                top_kw.append(keys[srno])
        return top_kw


class QuestionAnswerGenerator(ExtractKeyWords):


    def __init__(self, topic=None):
        super().__init__(topic)
        self.optn_gen = pt(hidden=True)
        self.glove = api.load('glove-wiki-gigaword-300')
        
        # self.url = "https://www.powerthesaurus.org/synonyms"
        # if hidden is None:
        #     hidden = False
        # if hidden:
        #     options = Options()
        #     options.headless = True
        #     self.driver = webdriver.Chrome(options=options)
        # else:
        #     self.driver = webdriver.Chrome()
        # self.filter = ['n.', 'v.', 'adj.', 'adv.', 'adj., n.']

    def generate_blank_questions(self):
        is_file = False
        path = self.folder_path
        files = os.listdir(path)
        if 'questions.pkl' in files:
            is_file = True
            file_name = os.path.join(path, 'questions.pkl')
            with open(file_name, 'rb') as f:
                questions_per_parra = pickle.load(f)
        if not is_file:
            kw_per_parra = self.filter_keywords_using_pos()
            sents_per_parra = self.sentences_per_parra()
            questions_per_parra = [None]*len(sents_per_parra)
            i = 0
            for kw_list, sent_list in zip(kw_per_parra, sents_per_parra):
                ques = []
                for kw in kw_list:
                    for sent in sent_list:
                        if kw in sent:
                            kw_id = sent.index(kw)
                            kw_len = len(kw)
                            replace_blank = ' '
                            for _ in range(0, kw_len):
                                replace_blank += '_'
                            q = (sent[: kw_id]
                                + replace_blank + sent[kw_id + kw_len:])
                            if q[0] == ' ':
                                q = q[1:]
                            q = q.capitalize()
                            kq_pair = (kw, q)
                            ques.append(kq_pair)
                questions_per_parra[i] = ques
                i += 1
                # save files_in_folder
                file_name = os.path.join(path, 'questions.pkl')
                with open(file_name, 'wb') as f:
                    pickle.dump(questions_per_parra, f)
        return questions_per_parra


    def generate_definition_questions(self):
        all_keywords = self.get_all_keywords()
        sents_per_parra = self.sentences_per_parra()
        # questions_per_parra = [None]*len(kw_per_parra)
        definition_questions = []
        definitions = {}
        for sents in sents_per_parra:
            for kw in all_keywords:
                for sent in sents:
                    # print(sent[:len(kw) + 10])
                    if kw + ' is a' in sent[:len(kw) + 10]:
                        q = "What is a " + kw + "?"
                        # def_q_and_a.append((q, sent))
                        definition_questions.append((kw, q))
                        definitions[kw] = sent
                    elif ' is called the ' + kw in sent:
                        q = "What is the " + kw + "?"
                        # def_q_and_a.append((q, sent))
                        definition_questions.append((kw, q))
                        definitions[kw] = sent
        return definition_questions, definitions


    # def initialize_final_options(self, keywords):
    #     final_options = {}
    #     for kw in keywords:
    #         final_options[kw] = {}
    #         i = 0
    #         while i <= 5:
    #             final_options[kw][str(i)] = ''
    #             i += 1
    #     return final_options


    # def generate_options(self):
    #     is_file = False
    #     path = self.folder_path
    #     files = os.listdir(path)
    #     if 'mcq_options.pkl' in files:
    #         is_file = True
    #         file_name = os.path.join(path, 'mcq_options.pkl')
    #         with open(file_name, 'rb') as f:
    #             self.mcq_options = pickle.load(f)
    #     if not is_file:
    #         all_keywords = self.get_all_keywords()
    #         final_options = self.initialize_final_options(all_keywords)
    #         self.mcq_options = {}
    #         not_found_internet = []
    #         not_names = []
    #         for keyword in all_keywords:
    #             if keyword in self.people_names:
    #                 name_options = []
    #                 name_options.insert(0, keyword)
    #                 rand_choice = random.sample(range(0, len(self.people_names)), 5)
    #                 for choice in rand_choice:
    #                     name_options.append(self.people_names[choice])
    #                 self.mcq_options[keyword] = name_options
    #             else:
    #                 not_names.append(keyword)
    #         options = self.optn_gen.search_for_meaning(not_names)
    #         for kw, opt in options.items():
    #             if opt == []:
    #                 not_found_internet.append(kw)
    #             else:
    #                 self.mcq_options[kw] = opt
    #         for kw, value in self.mcq_options.items():
    #             for srno, val in enumerate(value):
    #                 try:
    #                     final_options[kw][str(srno)] = val
    #                 except KeyError:
    #                     pass
    #         # print("MCQ Options: ", self.mcq_options)
    #         print("Final Options: ", final_options)
    #         print("Not found internet: ", not_found_internet)
    #         glove_options = self.generate_options_with_glove(not_found_internet)
    #         print("Glove options: ", glove_options)
        
        
    def generate_options_glove(self, keyword_list=None):
        options = {}
        if keyword_list is None:
            all_keywords = self.get_all_keywords()
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        else:
            all_keywords = keyword_list
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        # print("People Names: ", self.people_names)
        for kw in all_keywords:
            if kw not in self.people_names:
                words = kw.split()
                if len(words) == 1:
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            optn.append(sim_word[0])
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
                elif len(words) == 2:
                    meanings = ''
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            meaning = sim_word[0] + ' ' + words[1]
                            optn.append(meaning)
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
                else:
                    options[kw] = [kw]
                    sim_all_words = [None]*len(words)
                    for srno, word in enumerate(words):
                        optn = []
                        try:
                            sim_words = self.glove.most_similar(positive=[word]
                                                               ,topn=4)
                        except KeyError:
                            pass
                        for sim_word in sim_words:
                            optn.append(sim_word[0])
                        optn = optn[1:]
                        sim_all_words[srno] = optn
                    for _ in range(3):
                        rc = random.sample(range(0,3),3)
                        option = ''
                        for srno, word in enumerate(sim_all_words):
                            option += word[rc[srno]] + ' '
                            if srno + 1 == len(sim_all_words):
                                option = option[:-1]
                                options[kw].append(option)
        return options
    
        
    def generate_mcq_options(self):
        is_file = False
        path = self.folder_path
        files = os.listdir(path)
        if 'options.pkl' in files:
            is_file = True
            file_name = os.path.join(path, 'options.pkl')
            with open(file_name, 'rb') as f:
                final_options = pickle.load(f)
        if not is_file:
            all_keywords = self.get_all_keywords()
            final_options = {}
            not_found_internet = []
            not_names = []
            for keyword in all_keywords:
                if keyword in self.people_names:
                    name_options = []
                    name_options.insert(0, keyword)
                    rand_choice = random.sample(range(0, 
                                len(self.people_names)), 3)
                    for choice in rand_choice:
                        name_options.append(self.people_names[choice])
                    final_options[keyword] = name_options
                else:
                    not_names.append(keyword)
            options = self.optn_gen.search_for_meaning(not_names)
            for kw, opt in options.items():
                if opt == []:
                    not_found_internet.append(kw)
                elif len(opt) < 4:
                    not_found_internet.append(kw)
                else:
                    final_options[kw] = opt
            if len(not_found_internet) > 0:
                options = self.generate_options_glove(not_found_internet)
                for kw, opt in options.items():
                    final_options[kw] = opt
            file_name = os.path.join(path, 'options.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(final_options, f)
            # pprint.pprint(final_options)
        return final_options
            


    def generate_questions_top_kw(self, no_of_ques=None):
        if no_of_ques is None:
            no_of_ques = 15
        top_kw = self.get_top_keywords(5)
        # keyword_pos = self.get_pos_of_all_keywords()
        path = self.folder_path
        files = os.listdir(path)
        if 'people_names.pkl' in files:
            file_name = os.path.join(path, 'people_names.pkl')
            with open(file_name, 'rb') as f:
                people_names = pickle.load(f)
        # print(top_kw)
        questions = []
        for kw in top_kw[:no_of_ques]:
            if kw in people_names:
                q = "Who is " + kw + " ?"
                questions.append((kw, q))
            else:
                q = "What is " + kw + " ?"
                questions.append((kw, q))
        related_text = {}
        sents_per_parra = self.sentences_per_parra()
        for kw in top_kw[:no_of_ques]:
            related_text[kw] = []
            for sent_list in sents_per_parra:
                for sent in sent_list:
                    if kw in sent:
                        related_text[kw].append(sent)
            rt = related_text[kw]
            rt = rt[:3]
            related_text[kw] = rt
        updated_text = dict(related_text)
        kw_to_del = ''
        for key, val in related_text.items():
            if val == []:
                del updated_text[key]
                kw_to_del = key
                # print("Key: ",key)
        for kw, q in questions:
            if kw == kw_to_del:
                # print("KW: ",kw)
                idx = questions.index((kw, q))
                questions.pop(idx)
        return questions, updated_text


    def get_all_subjective_questions_answers(self):
        is_file = False
        path = self.folder_path
        files = os.listdir(path)
        # combined_questions = []
        # combined_answers = {}
        if 'subj_questions.pkl' in files:
            is_file = True
            file_name = os.path.join(path, 'subj_questions.pkl')
            with open(file_name, 'rb') as f:
                combined_questions = pickle.load(f)
            file_name = os.path.join(path, 'subj_answers.pkl')
            with open(file_name, 'rb') as f:
                combined_answers = pickle.load(f)
        # print("Starting debug")
        if not is_file:
            # q1, a1 = self.generate_definition_questions()
            combined_questions, combined_answers = self.generate_questions_top_kw()
            # print("Q2: ", q2)
            # print("A2: ", a2)

            file_name = os.path.join(path, 'subj_questions.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(combined_questions, f)
            file_name = os.path.join(path, 'subj_answers.pkl')
            with open(file_name, 'wb') as f:
                pickle.dump(combined_answers, f)
        return combined_questions, combined_answers


    


    # def get_similar_keywords(self, save_data=True, kw_list=None):
    #     if kw_list is None:
    #         keywords = self.filter_keywords_using_pos()
    #         similar_words = {}
    #         for kw_para in keywords:
    #             for kw in kw_para:
    #                 words = kw.split()
    #                 if len(words) == 1:
    #                     try:
    #                         similar = self.model.most_similar(positive=[kw],
    #                                                           topn=6)
    #                     except KeyError:
    #                         pass
    #                     synm = []
    #                     for sim in similar:
    #                         synm.append(sim[0])
    #                     # because most similar 1st word is always almost
    #                     # same as the word
    #                     synm = synm[1:]
    #                     # print(f"KW: {words} SimW: {synm}")
    #                     similar_words[kw] = synm
    #                 else:
    #                     for word in words:
    #                         try:
    #                             sim = self.model.most_similar(positive=[word],
    #                                                           topn= 6)
    #                         except KeyError:
    #                             pass
    #                         ss = []
    #                         for s in sim:
    #                             try:
    #                                 ss.append(s[0])
    #                                 similar_words[word] = ss[1:]
    #                             except TypeError:
    #                                 pass
    #         return keywords, similar_words
    #     else:
    #         for kw in kw_list:
    #             words = kw.split()
    #             if len(words) == 1:
    #                 try:
    #                     similar = self.model.most_similar(positive=[kw],
    #                                                       topn=6)
    #                 except KeyError:
    #                     pass
    #                 synm = []
    #                 for sim in similar:
    #                     synm.append(sim[0])
    #                 # because most similar 1st word is always almost
    #                 # same as the word
    #                 synm = synm[1:]
    #                 # print(f"KW: {words} SimW: {synm}")
    #                 similar_words[kw] = synm
    #             else:
    #                 for word in words:
    #                     try:
    #                         sim = self.model.most_similar(positive=[word],
    #                                                       topn= 6)
    #                     except KeyError:
    #                         pass
    #                     ss = []
    #                     for s in sim:
    #                         try:
    #                             ss.append(s[0])
    #                             similar_words[word] = ss[1:]
    #                         except TypeError:
    #                             pass
    #         return kw_list, similar_words


    # def initialize_options(self, keywords):
    #     options = {}
    #     for kw_list in keywords:
    #         for kw in kw_list:
    #             options[kw] = {}
    #             i = 0
    #             while i <= 3:
    #                 options[kw][str(i)] = ''
    #                 i += 1
    #     return options


    # def generate_options_with_glove(self, save_data=True, kw_list=None):
    #     if kw_list is None:
    #         keywords, sim_words = self.get_similar_keywords()
    #         options = self.initialize_options(keywords=keywords)
    #         for kw_list in keywords:
    #             for kw in kw_list:
    #                 options[kw]['0'] = kw
    #                 i = 1
    #                 rand_ints =  random.sample(range(0, 5), 3)
    #                 # print("RandInts!", rand_ints, len(rand_ints))
    #                 while i <= 3:
    #                     optional_word = ''
    #                     words = kw.split()
    #                     if len(words) == 1:
    #                         try:
    #                             options[kw][str(i)] = sim_words[
    #                                 words[0]][rand_ints[i - 1]]
    #                         except IndexError:
    #                             pass
    #                     elif len(words) == 2:
    #                         for srno, word in enumerate(words):
    #                             if srno == 0:
    #                                 try:
    #                                     optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                                 except IndexError:
    #                                     # print(e, sim_words[word])
    #                                     pass
    #                             elif srno == 1:
    #                                 optional_word += word + ' '
    #                         optional_word = optional_word[:-1]
    #                         options[kw][str(i)] = optional_word
    #                     else:
    #                         rand_choice = random.choice([True, False])
    #                         for srno, word in enumerate(words):
    #                             if rand_choice:
    #                                 if srno == 0:
    #                                     try:
    #                                         optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                                     except IndexError:
    #                                         pass
    #                                 elif srno == 1:
    #                                     optional_word += word + ' '
    #                                 else:
    #                                     try:
    #                                         optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                                     except IndexError:
    #                                         pass
    #                             else:
    #                                 if srno == 0:
    #                                     optional_word += word + ' '
    #                                 elif srno == 1:
    #                                     try:
    #                                         optional_word += sim_words[
    #                                             word][rand_ints[i - 1]] + ' '
    #                                     except IndexError:
    #                                         pass
    #                                 else:
    #                                     optional_word += word + ' '
    #                         optional_word = optional_word[:-1]
    #                         options[kw][str(i)] = optional_word
    #                     i += 1
    #     else:
    #         keywords, sim_words = self.get_similar_keywords(kw_list=kw_list)
    #         options = self.initialize_options(keywords=keywords)
    #         for kw in kw_list:
    #             options[kw]['0'] = kw
    #             i = 1
    #             rand_ints =  random.sample(range(0, 5), 3)
    #             # print("RandInts!", rand_ints, len(rand_ints))
    #             while i <= 3:
    #                 optional_word = ''
    #                 words = kw.split()
    #                 if len(words) == 1:
    #                     try:
    #                         options[kw][str(i)] = sim_words[
    #                             words[0]][rand_ints[i - 1]]
    #                     except IndexError:
    #                         pass
    #                 elif len(words) == 2:
    #                     for srno, word in enumerate(words):
    #                         if srno == 0:
    #                             try:
    #                                 optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                             except IndexError:
    #                                 # print(e, sim_words[word])
    #                                 pass
    #                         elif srno == 1:
    #                             optional_word += word + ' '
    #                     optional_word = optional_word[:-1]
    #                     options[kw][str(i)] = optional_word
    #                 else:
    #                     rand_choice = random.choice([True, False])
    #                     for srno, word in enumerate(words):
    #                         if rand_choice:
    #                             if srno == 0:
    #                                 try:
    #                                     optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                                 except IndexError:
    #                                     pass
    #                             elif srno == 1:
    #                                 optional_word += word + ' '
    #                             else:
    #                                 try:
    #                                     optional_word += sim_words[word][rand_ints[i - 1]] + ' '
    #                                 except IndexError:
    #                                     pass
    #                         else:
    #                             if srno == 0:
    #                                 optional_word += word + ' '
    #                             elif srno == 1:
    #                                 try:
    #                                     optional_word += sim_words[
    #                                         word][rand_ints[i - 1]] + ' '
    #                                 except IndexError:
    #                                     pass
    #                             else:
    #                                 optional_word += word + ' '
    #                     optional_word = optional_word[:-1]
    #                     options[kw][str(i)] = optional_word
    #                 i += 1
    #     return options
    
    
    def restructure_topic(self, topic):
        # last_char = topic[-1]
        # if last_char == 's':
        #     topic = topic[:-1]
        topic_words = topic.split()
        topic = ''
        for word in topic_words:
            topic += word.capitalize() + ' '
        topic = topic[:-1]
        return topic


class ConsoleUserInterface:

    def display_parra(self, no):

        para = self.qag.paras_in_str
        print(para[no])
        return para[no]


    def get_topic_from_user(self):
        print("\nWelcome to this Reflective Learning App.\n")
        print("""You can either choose to learn from preloaded topics,
or enter the topic you want to learn.
              """)
        while True:
            print("""\nEnter v to view preloaded topics,
or n to learn a specific topic and q to quit\n""")
            user_input = input("Enter your choice: ")
            if user_input == 'q':
                break
            elif user_input == 'v':
                topics = self.show_existing_topics()
                print("\nExisting topics are: \n")
                for srno, topic in enumerate(topics):
                    print(f"Press {srno} to select {topic}")
                try:
                    existing_topic = input("Enter your choice: ")
                    topic = topics[int(existing_topic)]
                    break
                except Exception as e:
                    print("Error: ", e)
            elif user_input == 'n':
                topic = input("\nPlease enter the topic you want to learn: ")
                break
            else:
                print("\nInvalid input, please try again...")
                pass
        last_char = topic[-1]
        if last_char == 's':
            topic = topic[:-1]
        topic_words = topic.split()
        topic = ''
        for word in topic_words:
            topic += word.capitalize() + ' '
        topic = topic[:-1]
        print("Topic is: ", topic)
        return topic


    def show_existing_topics(self):
        path = os.path.dirname(os.path.abspath(__file__))
        path_to_topic = os.path.join(path, 'Topics')
        topics = os.listdir(path_to_topic)
        return topics


    def start_learning(self):
        topic = self.get_topic_from_user()
        # self.kw = ExtractKeyWords(topic)
        # self.qg = QuestionGenerator(topic)
        # self.ag = AnswerGenerator(topic)
        self.qag = QuestionAnswerGenerator(topic)

        self.no_of_parras = len(self.qag.paragraphs)
        self.main_learning()


    def main_learning(self):


        questions = self.qag.generate_blank_questions()
        options = self.qag.generate_options_with_glove()
        self.correct_ans = 0
        self.wrong_ans = 0
        print(f"\nThis topic has {self.no_of_parras} parras.\n")

        while True:
            start = input("\nPress y to start learning, press q to quit: ")
            start = start.lower()
            if start == 'y':
                to_learn = int(input("\nEnter the number of parras you wish to learn now: "))
                if to_learn <= self.no_of_parras:
                    for i in range(0, to_learn):
                        q_in_para = questions[i]
                        print("\nPlease read the following text and answer the questions:\n")
                        print(f"\nDisplaying parra [{i}/{self.no_of_parras}]\n")
                        para = self.display_parra(i)
                        sentences = para.split(sep='.')
                        user_input = input("\nEnter n for next step: ")
                        user_input = user_input.lower()
                        if user_input == 'n':
                            if len(sentences) <= 3:
                                no_of_ques = 2
                            elif 3 < len(sentences) <= 6:
                                no_of_ques = 4
                            else:
                                no_of_ques = 5
                            rand_ques =  random.sample(range(0, len(q_in_para)),
                                no_of_ques)
                            for no in rand_ques:
                                kw, q = q_in_para[no]
                                print("\nQuestion: \n", q,"\n")
                                rand_optns = random.sample(range(0, 4), 4)
                                correct_optn = rand_optns.index(0)
                                print("\nOptions: \n")
                                for op_no in range(0, len(rand_optns)):
                                    print(f"Option {str(op_no)}: ",
                                          options[kw][str(rand_optns[op_no])])
                                while True:
                                    answer = input("Enter the correct option no: ")
                                    if 0 <= int(answer) <= 3:
                                        if int(answer) == correct_optn:
                                            print("\nCorrect Answer\n")
                                            self.correct_ans += 1
                                            break
                                        else:
                                            print("\nWrong Answer, correct Ans is :", kw,"\n")
                                            self.wrong_ans += 1
                                            break
                                    else:
                                        print("\nInvalid Option.\n")
                        elif user_input == 'q':
                            break
                        elif user_input == 'p':
                            pass
                    print(f"Score: {self.correct_ans}/{self.correct_ans + self.wrong_ans}")
                else:
                    print("Invalid input...")
                    re_enter = input("Enter valid number or press q to quit: ")
                    re_enter = re_enter.lower()
                    if re_enter == 'q':
                        break
                    else:
                        to_learn = int(re_enter)
            elif start == 'q':
                break
            else:
                continue


class TestOptionGen(ExtractKeyWords):
    def __init__(self, topic):
        super().__init__(topic)
        # self.optn_gen = og.PowerTheasurus()
        self.glove = api.load('glove-wiki-gigaword-300')
        self.google = api.load('word2vec-google-news-300')
        self.optn_gen = pt(hidden=False)


    def generate_options(self):
        options = {}
        all_keywords = self.get_all_keywords()
        keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        print("People Names: ", self.people_names)
        for kw in all_keywords:
            if kw not in self.people_names:
                words = kw.split()
                if len(words) == 1:
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            optn.append(sim_word[0])
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
                elif len(words) == 2:
                    meanings = ''
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            meaning = sim_word[0] + ' ' + words[1]
                            optn.append(meaning)
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
        print(options)
        return options
        # return not_found, glove, google
        
        
    def generate_options_glove(self, keyword_list=None):
        options = {}
        if keyword_list is None:
            all_keywords = self.get_all_keywords()
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        else:
            all_keywords = keyword_list
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        print("People Names: ", self.people_names)
        for kw in all_keywords:
            if kw not in self.people_names:
                words = kw.split()
                if len(words) == 1:
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            optn.append(sim_word[0])
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
                elif len(words) == 2:
                    meanings = ''
                    optn = []
                    try:
                        sim_words = self.glove.most_similar(positive=[words[0]],
                                                        topn=4)
                    except KeyError:
                        pass
                    try:
                        for sim_word in sim_words:
                            meaning = sim_word[0] + ' ' + words[1]
                            optn.append(meaning)
                    except Exception:
                        pass
                    optn = optn[1:]
                    optn.insert(0, kw)
                    options[kw] = optn
                elif len(words) == 3:
                    pass
                else:
                    pass
        return options
                    
    def get_options(self, keyword_list=None):
        final_options = {}
        # options = {}
        if keyword_list is None:
            all_keywords = self.get_all_keywords()
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        else:
            all_keywords = keyword_list
            keyword_pos = self.get_pos_of_all_keywords(all_keywords)
        not_found_internet = []
        not_names = []
        for keyword in all_keywords:
            if keyword in self.people_names:
                name_options = []
                name_options.insert(0, keyword)
                rand_choice = random.sample(range(0, len(self.people_names)), 4)
                for choice in rand_choice:
                    name_options.append(self.people_names[choice])
                final_options[keyword] = name_options
            else:
                not_names.append(keyword)
        options = self.optn_gen.search_for_meaning(not_names)
        for kw, opt in options.items():
            if opt == []:
                not_found_internet.append(kw)
            elif len(opt) < 4:
                not_found_internet.append(kw)
            else:
                final_options[kw] = opt
        if len(not_found_internet) > 0:
            options = self.generate_options_glove(not_found_internet)
            for kw, opt in options.items():
                final_options[kw] = opt
        print(final_options)
        return final_options


class NewTopicCreator(QuestionAnswerGenerator):
    def __init__(self, topic):
        
        topic = self.restructure_topic(topic)
        print("Topic chosen: ", topic)
        super().__init__(topic)
        # self.make_dir_for_topic()
        # self.clean_text(save_data=True)
        # self.get_all_keywords()
        # self.generate_blank_questions()
        # self.generate_mcq_options()
        self.get_all_subjective_questions_answers()
        
        
class SubQuesChecker:
    def __init__(self):
        self.sent_model = sent_encoder.load_model('en_use_lg')
        
        
    def compare_2_sentences(self, sent1, sent2):
        doc1 = self.sent_model(sent1)
        doc2 = self.sent_model(sent2)
        similarity = doc1.similarity(doc2)
        # print("Similarity: ", similarity)
        return similarity
        

if __name__ == "__main__":
    obj = ExtractKeyWords(topic='Artificial Intelligence')
    ckw = obj.compare_keywords()
    pass
