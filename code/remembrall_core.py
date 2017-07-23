import nltk
from fuzzywuzzy import fuzz
from remembrall_db_helper import PostgresHelper
from remembrall_usr_table import UserTableManager
import remembrall_rule_engine
import logging as log
import re

log.basicConfig(level=log.DEBUG)
import random
import datetime
import remembrall_util

config_dict = remembrall_util.get_configs()
response_dict = remembrall_util.load_saved_response_messages()
bot_specific_question_phrases = remembrall_util.load_bot_specific_questions()


known_qa_dict = remembrall_rule_engine.known_qa_dict
q_set = {"why", "what", "when", "who", "where", "how", "which"}

ruleEngine = remembrall_rule_engine.RuleEngine()

class BestMatcher(object):

    def __init__(self, list_of_dict, q_message):
        self.list_of_dict = list_of_dict
        self.result_dict = dict()
        self.max_count = 0
        self.q_message = q_message
        self.max_total_score = 0
        self.max_total_score_id = -1
        self.confident = 1

    def restructure_list_of_dict(self):
        for result_d in self.list_of_dict:
            message_id = int(result_d['msg_id'])
            if message_id not in self.result_dict:
                self.result_dict[message_id] = result_d
                self.result_dict[message_id]['count'] = 0
            count = self.result_dict[message_id]['count']
            self.result_dict[message_id]['count'] += 1
            if self.max_count < count + 1:
                self.max_count = count + 1
        print self.result_dict


    def calculate_score(self):
        for message_id in self.result_dict:
            curr_message = self.result_dict[message_id]['msg_text']
            self.result_dict[message_id]['fuzzy_score'] = \
                fuzz.token_sort_ratio(curr_message, self.q_message)
            self.result_dict[message_id]['count_score'] = \
                (100*self.result_dict[message_id]['count'])/self.max_count
            total_score = self.result_dict[message_id]['fuzzy_score'] + \
                          self.result_dict[message_id]['count_score']
            self.result_dict[message_id]['total_score'] = total_score
            if total_score > self.max_total_score:
                self.max_total_score = total_score
                self.max_total_score_id = message_id

    def find_best_match(self):
        self.restructure_list_of_dict()
        self.calculate_score()
        print self.result_dict[self.max_total_score_id]
        #todo: total score

        if self.result_dict[self.max_total_score_id]['fuzzy_score'] < 55:
            self.confident = 0
        return self.result_dict[self.max_total_score_id]

class MessageTexts(object):

    def __init__(self, message_text, normalized_message, tokenized_message, normalized_tokens):

        self.message_text = message_text
        self.normalized_message = normalized_message
        self.tokenized_message = tokenized_message
        self.normalized_tokens = normalized_tokens



class Message(object):
    def __init__(self, message_text, usr_id):
        self.usr_id = usr_id
        self.message_text = message_text
        self.normalized_message = self.normalize_message()
        self.tokenized_message = nltk.word_tokenize(self.message_text)
        self.normalized_tokens = nltk.word_tokenize(self.normalized_message)
        self.nouns = list()
        self.verbs = list()
        self.insert_dict_list = list()
        self.message_type = "A"
        self.message_id = 0
        self.messagetexts = MessageTexts(self.message_text, self.normalized_message, self.tokenized_message, self.normalized_tokens)

    def get_profile(self):
        userTableManager = UserTableManager()
        exists = userTableManager.profile_exists(self.usr_id)
        if exists is False:
            userTableManager.process(self.usr_id)

    def remove_bot_specific_words(self):
        pass

    def normalize_message(self):
        regex = re.compile('[^a-z ]')
        return regex.sub('', self.message_text.lower())

    def identify_rule_based(self):
        if self.tokenized_message[-1] == "?":
            self.message_type = "Q"
            return "Q"
        else:

            for token in self.tokenized_message:
                if token.lower() in q_set:
                    self.message_type = "Q"

    def identify_message_type(self):
        self.message_type = ruleEngine.apply_rules(self.messagetexts)

    def get_response_message(self):
        if self.message_type in {'A', 'T', 'C', 'I', 'B', 'G', 'N'}:
            return random.choice(response_dict[self.message_type])
        elif self.message_type == "K":
            if self.normalized_message in known_qa_dict:
                return known_qa_dict[self.normalized_message]
            else:
                return known_qa_dict[self.message_text]

        else:
            return random.choice(response_dict[self.A])

    def insert_in_log_table(self):
        postgres = PostgresHelper()
        curr_max = postgres.postgres_select_max_from(
            table_name=config_dict['LOG_TABLE'],
            column_name="msg_id")
        self.message_id = curr_max + 1

        insertion_dict = [{'usr_id': self.usr_id, 'msg_id': self.message_id,
                           'msg_text': self.message_text,
                           'msg_typ':self.message_type,
                           'cr_ts': str(datetime.datetime.now())}]
        postgres.postgres_insert_dictionary_list(
            dict_list=insertion_dict, table_name=config_dict['LOG_TABLE'])
        postgres.con.close()

    def construct_remember_dict_list(self):
        if len(self.verbs) == 0:
            self.verbs.append("V")

        for n in self.nouns:
            for v in self.verbs:
                index_dict = dict()
                index_dict['noun'] = n
                index_dict['verb'] = v
                index_dict['adjective'] = "N/A"
                index_dict['locn_dimnsn'] = "N/A"
                index_dict['time_dimnsn'] = "N/A"
                index_dict['msg_text'] = self.message_text
                index_dict['msg_id'] = self.message_id
                index_dict['usr_id'] = self.usr_id
                index_dict['cr_ts'] = str(datetime.datetime.now())
                self.insert_dict_list.append(index_dict)

    def tag_pos(self):
        text = self.tokenized_message
        tagged = nltk.pos_tag(text)
        print "tagged", tagged

        for tag in tagged:
            if tag[1][0] == 'N' or tag[1] == 'PRP' or tag[1] == 'DT':
                n = remembrall_util.normalize_and_stem(tag[0])
                self.nouns.append(n)
            elif tag[1][0] == 'V' or tag[1][0] == 'VBP' or tag[1][0] == 'VB':
                v = remembrall_util.normalize_and_stem(tag[0])
                self.verbs.append(v)

    def rephrase_answer(self, best_match_message):
        #rules to rephrase the answer
        best_match_message = best_match_message.replace("My", "Your")\
            .replace("my", "your").replace("I ", "You")

        return best_match_message

    def remember(self):
        postgres = PostgresHelper()
        self.tag_pos()
        print "Nouns:", self.nouns
        print "Verbs", self.verbs
        self.construct_remember_dict_list()

        postgres.postgres_insert_dictionary_list(
            table_name=config_dict['MAIN_TABLE'],
            dict_list=self.insert_dict_list)
        log.debug("remembered")
        postgres.con.close()
        try:
            return self.get_response_message()
        except Exception as err:
            print "error in fetching response message in remember()"
            return "Alright, I'll remember that!"

    def seek(self):
        postgres = PostgresHelper()
        self.tag_pos()

        print "Nouns:", self.nouns
        print "Verbs", self.verbs
        if len(self.nouns) == 0:
            print "Sorry, I cannot understand"
            return "Sorry, I cannot understand"

        condition = "WHERE noun in ({}) AND usr_id = '{}'".format(','.join('%s'
                                            for n in self.nouns), self.usr_id)

        answers = postgres.postgres_select(table_name=config_dict['MAIN_TABLE'],
                                           req_column_list='*',
                                           return_dict=True,
                                           condition=condition,
                                           parameters=self.nouns)
        postgres.con.close()
        print answers
        print ""

        if len(answers) > 0:
            bestMatcher = BestMatcher(answers, self.message_text)
            best_match_dict = bestMatcher.find_best_match()

            if bestMatcher.confident == 0:
                best_match_msg = ("I'm not very "
                                "sure but I think this is what you are "
                                "looking for: " + best_match_dict['msg_text'])
                return best_match_msg
            else:
                best_match_msg =  best_match_dict['msg_text']
                return self.rephrase_answer(best_match_msg)
        return "I'm sorry, I don't know the answer to that."

if __name__ == '__main__':
    while(True):
        text = raw_input("Print your message:")
        if text==-1:
            break
        msg = Message(text,"urjit")
        #msg.identify_rule_based()

        msg.identify_message_type()
        msg.insert_in_log_table()
        if msg.message_type in {'T', 'I', 'C', 'K', 'B', 'G', 'N'}:
            try:
                response_message_text=msg.get_response_message()
            except LookupError, e:
                print "Lookup Error", str(e)
                response_message_text = msg.remember()

        elif msg.message_type == 'Q':
            response_message_text = msg.seek()

        else:
            response_message_text = msg.remember()
        print response_message_text