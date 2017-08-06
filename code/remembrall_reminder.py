import os
import re
import json
from natty import DateParser
from datetime import datetime, timedelta
import remembrall_util

config_dict = remembrall_util.get_configs()
class Reminders(object):
    def __init__(self):
        self.date_result = None
        self.day = ""
        self.month = ""
        self.year = ""
        self.hour = ""
        self.min = ""

    def is_reminder(self, text):
        result = DateParser(text).result()
        print result
        if len(result) > 0:
            self.date_result = result[0]
            return True
        return False

    def extract_date_time(self):
        self.year = self.date_result.year
        self.month = self.date_result.month
        self.day = self.date_result.day
        self.hour = self.date_result.hour
        self.min = self.date_result.minute


if __name__ == "__main__":
    reminder = Reminders()
    print reminder.is_reminder("Remind me to go there on Nov 2")
    print reminder.year
    while(True):
        ip = raw_input("Enter here:")

        print reminder.is_reminder(ip)
        reminder.extract_date_time()
        print reminder.date_result
        print "Y:", reminder.year, "M:", reminder.month, "D:", reminder.day, "H:", reminder.hour, "M:", reminder.min




