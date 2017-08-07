import remembrall_util
from remembrall_msg_type_classifier import MessageClassifier
from remembrall_reminder import Reminders

known_qa_dict = remembrall_util.load_saved_response_known_qa()
reminder = Reminders()

class RuleEngine(object):
    def __init__(self):
        self.rules_list = [RuleGreeting(), RuleInvalid(), RuleThankYou(), RuleKnownQA(), RuleBotSpecific(),
                           RuleReminder(), RuleClassifier(), RuleShortMessage()]
        self.rules = sorted((rule for rule in self.rules_list), key=lambda x: x.priority)

    def apply_rules(self, message_texts):

        print "normalized_msg_text", message_texts.normalized_message,
        
        for rule in self.rules:
            success = rule.apply(message_texts)
            if success is True:
                return rule.rule_type

class Rule(object):

    def __init__(self, type='BLANK', priority=100):
        self.rule_type = type
        self.priority = priority

    def apply(self, message_texts):
        pass



class RuleGreeting(Rule):
    #GREETING
    def __init__(self):
        Rule.__init__(self, type="G", priority=1)

        self.greeting_set = {'hi', 'hey', 'hello', 'greetings', 'bonjour'}
        self.day_time_set = {"morning", "afternoon", "evening", "night", "noon"}

    def check_for_greeting(self, message_texts):
        for token in message_texts.tokenized_message:
            if token.lower() in self.greeting_set:
                return True
        if "good" in message_texts.normalized_tokens and len(message_texts.normalized_tokens) < 4:
            for token in message_texts.normalized_tokens:
                if token in self.day_time_set:
                    return True
        return False

    def apply(self, message_texts):
        if self.check_for_greeting(message_texts) is True:
            print "Applied Rule:", "G"

            return True
        return False


class RuleKnownQA(Rule):

    def __init__(self):
        Rule.__init__(self, type="K", priority=2)
        self.known_qa_dict = known_qa_dict

    def apply(self, message_texts):
        if message_texts.normalized_message in self.known_qa_dict:
            print "Applied Rule:", "K"
            return True

        if message_texts.message_text in self.known_qa_dict:
            print "Applied Rule:", "K"

            return True

        return False


class RuleInvalid(Rule):
    #INVALID
    def __init__(self):
        Rule.__init__(self, type="N", priority=3)

    def apply(self, message_texts):
        if len(message_texts.message_text) < 3:
            self.message_type = "N"
            print "Applied Rule:", "N"

            return True
        return False


class RuleThankYou(Rule):

    def __init__(self):
        Rule.__init__(self, type="T", priority=4)
        self.thank_set = {"thank you!", "thanks!", "thanks", "thank you", "thank u"}

    def apply(self, message_texts):
        if message_texts.message_text.lower() in self.thank_set:
            print "Applied Rule:", "T"

            return True
        return False



class RuleBotSpecific(Rule):

    def __init__(self):
        Rule.__init__(self, type="B", priority=5)
        self.bot_specific_question_phrases = remembrall_util.load_bot_specific_questions()

    def apply(self, message_texts):
        for bot_spec_phrase in self.bot_specific_question_phrases:
            if message_texts.normalized_message.startswith(bot_spec_phrase):
                print "Applied Rule:", "B"

                return True

        return False


class RuleReminder(Rule):
    #REMINDER
    def __init__(self):
        Rule.__init__(self, type="R", priority=6)

    def apply(self, message_texts):
        if reminder.is_reminder(text=message_texts.message_text) is True:
            print "Applied Rule: ", "R"
            return True
        return False


class RuleShortMessage(Rule):
    def __init__(self):
        Rule.__init__(self, type="N", priority=991)

    def apply(self, message_texts):
        if len(message_texts.normalized_tokens) < 3:
            self.message_type = "N"
            print "Applied Rule:", "6"

            return True
        return False



class RuleClassifier(Rule):

    def __init__(self):
        Rule.__init__(self, priority=99)
        self.bot_specific_question_phrases = remembrall_util.load_bot_specific_questions()

    def apply(self, message_texts):
        msg_classifier = MessageClassifier()
        self.message_type = msg_classifier.predict_message_type(message_texts.message_text)

        if self.message_type is 'A':
            rule_short_message = RuleShortMessage()
            if rule_short_message.apply(message_texts) is True:
                self.message_type = 'N'

        self.rule_type = self.message_type
        print "Applied Rule:" , "classifier"
        return True


if __name__ == '__main__':
    from remembrall_core import Message

    message = Message(message_text="Good Morning", usr_id="abc")
    ruleFactory = RuleEngine()
    print ruleFactory.apply_rules(message.messagetexts)

    message = Message(message_text=":)", usr_id="abc")
    print ruleFactory.apply_rules(message.messagetexts)

    message = Message(message_text="Hi!", usr_id="abc")
    print ruleFactory.apply_rules(message.messagetexts)

    message = Message(message_text="How are you?", usr_id="abc")
    print ruleFactory.apply_rules(message.messagetexts)

    message = Message(message_text="magic", usr_id="abc")
    print ruleFactory.apply_rules(message.messagetexts)


