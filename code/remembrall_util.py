import os, os.path
import subprocess
from nltk.stem import SnowballStemmer
config_dict={}
stemmer = SnowballStemmer(language="english")
def normalize_and_stem(word):
    return stemmer.stem(word.lower())

def read_os_environment_parameters():
    for variable_key in os.environ:
        config_dict[variable_key] = os.environ[variable_key]

def read_config_file():
    read_os_environment_parameters()
    config_file_path = os.path.join(config_dict['PARENT_DIR'], "config/remembrall.properties")
    print config_file_path
    # try:
    with open(config_file_path) as f:
        for line in f:
            if line is not None and line.strip() != "":
                config_dict[line.strip().split("=")[0]] = \
                    line.strip().split("=")[1]

def get_configs():
    read_config_file()
    read_os_environment_parameters()
    return config_dict

def load_saved_response_known_qa():
    known_qa_dict = dict()
    response_file_path = os.path.join(
        config_dict['PARENT_DIR'],
        config_dict['known_qa'+'_response_file'])

    try:
        with open(response_file_path) as f:
            for line in f:
                known_qa_dict[line.split("=")[0].lower()] = line.split("=")[1]
    except Exception, e:
        print str(e)
        print "Error! Could not load saved known qa"
    return known_qa_dict


def load_bot_specific_questions():
    bot_specifc_questions = list()
    question_file_path = os.path.join(
        config_dict['PARENT_DIR'],
        config_dict['bot_specific_questions'])
    try:
        with open(question_file_path) as f:
            for line in f:
                bot_specifc_questions.append(line.strip())
    except Exception, e:
        print str(e)
        print "Error! Could not load bot specific questions"
    return bot_specifc_questions

def load_saved_response_messages():
    response_messages = dict()
    message_types = ['A', 'C', 'T', 'I', 'B', 'G', 'N']
    for message_type in message_types:
        response_file_path = os.path.join(
            config_dict['PARENT_DIR'],
            config_dict[message_type+'_response_file'])
        try:
            with open(response_file_path) as f:
                response_list = list()
                for line in f:
                    line = line.strip()
                    if line != "":
                        response_list.append(line)
            response_messages[message_type] = response_list
        except:
            print "Error! Could not load saved messages error!"

            #default messages
            response_messages['A'] = ["Alright, I'll remember that!"]
            response_messages['C'] = ["Thank you :)"]
            response_messages['I'] = ["I'm sorry, I do not follow. Could you "
                                      "please rephrase?"]
            response_messages['T'] = ["You're welcome :)"]
            response_messages['G'] = ["Hello :)"]
            response_messages['N'] = ["I'm sorry, right now, I am better at understaning complete sentences. Could you"
                                       " try rephrasing?"]
            return response_messages
    return response_messages

def fetch_jars():
    jar_path=os.path.join(config_dict['PARENT_DIR'], config_dict['su_jars_path'])
    if len([name for name in os.listdir(jar_path) if os.path.isfile(name)]) < 2:
        return_code = subprocess.call([os.path.join(config_dict['PARENT_DIR'], config_dict['jar_collector'])])
        print return_code


if __name__ == '__main__':
    print get_configs()
    print fetch_jars()