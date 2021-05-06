# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 14:01:19 2021

@author: sukrut
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


class FindMeanings:


    def __init__(self, hidden=None):
        self.url = "https://www.thesaurus.com/"
        self.suggestion_start = "Did you mean"
        self.suggestion_end = "More"
        self.start_clean = "OTHER WORDS FOR "
        if hidden is None:
            hidden = False
        if hidden:
            options = Options()
            options.headless = True
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()


    def search_meanings(self, keyword):
        if type(keyword) == str:
            is_single_word = True
        elif type(keyword) == list:
            is_single_word = False
        if is_single_word:
            self.driver.get(self.url)
            try:
                search = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.ID, "searchbar_input"))
                    )
                search.send_keys(keyword, Keys.RETURN)
                try:
                    meanings = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.ID, "meanings"))
                        )
                    text = meanings.text
                    # print(text)
                    # time.sleep(5)
                    if "TRY " + keyword + " IN A SENTENCE BELOW" in text:
                        id_waste = text.index('TRY')
                    elif "MOST RELEVANT" in text:
                        id_waste = text.index("MOST")
                    text = text[:id_waste - 1]
                    words = text.split('\n')
                    self.meanings = words[1:]
                    # print("Meanings: ", self.meanings)
                    is_meaning_found = True
                except Exception:
                    is_meaning_found = False
                    try:
                        suggestion = self.driver.find_element_by_class_name(
                            "spell-suggestions")
                        suggestion_text = suggestion.text
                        s_end = suggestion_text.index(self.suggestion_end)
                        new_keyword = suggestion_text[
                            len(self.suggestion_start) + 1:s_end]
                        self.search_meanings(new_keyword)
                    except Exception:
                        self.driver.quit()
            except Exception:
                pass
                # self.driver.quit()
            finally:
                self.driver.quit()
            if is_meaning_found:
                return self.meanings
        else:
            options = {}
            for srno, kw in enumerate(keyword):
                self.driver.get(self.url)
                try:
                    search = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.ID, "searchbar_input"))
                        )
                    search.send_keys(kw, Keys.RETURN)
                    try:
                        meanings = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.ID, "meanings"))
                        )
                        text = meanings.text
                        # print(text)
                        words = text.split('\n')
                        if "TRY " + kw + " IN A SENTENCE BELOW" in words:
                            id_1 = words.index("TRY " + kw + " IN A SENTENCE BELOW")
                            words.pop(id_1)
                        if "MOST RELEVANT" in words:
                            id_2 = words.index("MOST RELEVANT")
                            words.pop(id_2)
                        self.meanings = words[1:]
                        options[kw] = self.meanings
                    except Exception:
                        suggestion = self.driver.find_element_by_class_name(
                        "spell-suggestions")
                        suggestion_text = suggestion.text
                        s_end = suggestion_text.index(self.suggestion_end)
                        n_kw = suggestion_text[
                            len(self.suggestion_start) + 1:s_end]
                        # print("Reached here:", n_kw)
                        try:
                            search_bar = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((By.ID, "searchbar_input"))
                            )
                            search_bar.clear()
                            search_bar.send_keys(n_kw, Keys.RETURN)
                            try:
                                meanings = WebDriverWait(self.driver, 2).until(
                                    EC.presence_of_element_located((By.ID, "meanings"))
                                    )
                                time.sleep(3)
                                text = meanings.text
                                # print(text)
                                words = text.split('\n')
                                if "TRY " + kw + " IN A SENTENCE BELOW" in words:
                                    id_1 = words.index("TRY " + kw + " IN A SENTENCE BELOW")
                                    words.pop(id_1)
                                if "MOST RELEVANT" in words:
                                    id_2 = words.index("MOST RELEVANT")
                                    words.pop(id_2)
                                self.meanings = words[1:]
                                options[kw] = self.meanings
                            except Exception:
                                self.driver.back()
                        except Exception:
                            self.driver.back()
                except Exception:
                    self.driver.back()
            self.driver.quit()
            return options


    def search_further_meanings(self, word):
        print("ENtered")
        all_links = []
        useful_links = []
        links = self.driver.find_elements_by_tag_name('a')
        for link in links:
            all_links.append(link.get_attribute("href"))
        all_links = filter(None, all_links)
        for link in all_links:
            if self.meanings[0] in link:
                useful_links.append(link)
        self.driver.get(useful_links[0])
        r_words = self.driver.find_elements_by_tag_name('ul')
        raw_words = []
        for word in r_words:
            raw_words.append(word.text)
        pross_words = []
        for word in raw_words:
            if word != '':
                if not word[0].isupper():
                    if '\n' in word:
                        pross_words.append(word.split('\n'))
        total_words = []
        for lis in pross_words:
            total_words.extend(lis)
        total_words = set(total_words)
        print("total words: ", total_words)
        return total_words


class GoogleMeanings:


    def __init__(self, hidden=None):
        self.url = 'https://www.google.com'
        if hidden is None:
            hidden = False
        if hidden:
            options = Options()
            options.headless = True
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()


    def google_search(self, list_kw=None):
        self.driver.get(self.url)
        #active the iframe and click the agree button
        WebDriverWait(self.driver, 1).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe")))
        agree = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="introAgreeButton"]/span/span')))
        agree.click()
        #back to the main page
        self.driver.switch_to.default_content()
        if list_kw is not None:
            assert type(list_kw) == list
            for kw in list_kw:
                search = self.driver.find_element_by_class_name('gLFyf')
                search.send_keys(kw, Keys.RETURN)


class PowerTheasurus:


    def __init__(self, hidden=None):
        self.url = "https://www.powerthesaurus.org/synonyms"
        if hidden is None:
            hidden = False
        if hidden:
            options = Options()
            options.headless = True
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()
        self.filter = ['n.', 'v.', 'adj.', 'adv.', 'adj., n.', 'n., v.', 'n., adj.', 'v., n.']


    def search_for_meaning(self, kw_list):
        assert type(kw_list) == list
        options = {}
        for srno, kw in enumerate(kw_list):
            self.driver.get(self.url)
            try:
                search = self.driver.find_element_by_xpath('//*[@id="header"]/div/div[1]/div[2]/div/div/form/div/input')
                search.clear()
                search.send_keys(kw, Keys.RETURN)
                time.sleep(1)
                self.url = self.driver.current_url
                self.driver.get(self.url)
                time.sleep(1)
                meanings = self.driver.find_elements_by_xpath('//*[@id="app"]/div[3]/div[3]/main/div[2]')
                raw_text = ''
                for meaning in meanings:
                    raw_text += meaning.text
                # print("Raw text: ", raw_text)
                words = raw_text.split(sep='\n')
                # print(words)
                filtered_meanings = []
                for word in words:
                    if not word[0] == '#' and word not in self.filter and kw not in word:
                        filtered_meanings.append(word)
                # options[kw] = filtered_meanings.insert(0, kw)
                filtered_meanings.insert(0, kw)
                options[kw] = filtered_meanings[:4]
                # search.clear()
            except IndexError:
                options[kw] = []
            except Exception:
                pass
        self.driver.quit()
        return options

if __name__ == "__main__":
    fm = PowerTheasurus()
    options = fm.search_for_meaning(['distant observer', 'supermassive black hole',  'milky way'])

    print(options)
