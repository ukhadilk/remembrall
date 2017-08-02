import os
import re
import json
from sutime import SUTime
from datetime import datetime, timedelta
import remembrall_util

config_dict = remembrall_util.get_configs()
class Reminders(object):
    def __init__(self):
        remembrall_util.fetch_jars()
        self.jar_files = os.path.join(config_dict['PARENT_DIR'], config_dict['su_jars_path'])
        print "Printing available jars: "
        for name in os.listdir(self.jar_files):
            print name
        self.sutime = SUTime(jars=self.jar_files, mark_time_ranges=False)
        self.curr_time = []
        self.curr_type = ""
        self.curr_val = ""
        self.reminder_date = "" #yyyy-mm-dd
        self.reminder_time = "" ##hh:mm (24 hour clock)

    def is_reminder(self, text):
        self.curr_times = []
        times = self.sutime.parse(text)
        if len(times) > 0:
            self.curr_time = times[0]
            self.curr_type = self.curr_time['type']
            self.curr_val = self.curr_time['value']
            return True
        return False

    def extract_date_time(self):
        if self.curr_type == "TIME":
            self.reminder_date = self.curr_val.split("T")[0]
            self.reminder_time = self.curr_val.split("T")[1]
        elif self.curr_type == "DATE":
            self.reminder_date = self.curr_val.split("T")[0]
            self.reminder_time = "00:00:00"
        elif self.curr_type == "DURATION":
            minutes = 0
            if "H" in self.curr_val:
                hours = float(re.findall('\d+', self.curr_val)[0])
                minutes = hours * 60
            else:
                minutes = float(re.findall('\d+', self.curr_val)[0])

            reminder_time = datetime.now() + timedelta(minutes=minutes)
            self.reminder_date = reminder_time.date()
            self.reminder_time = reminder_time.time()
        print self.reminder_date
        print self.reminder_time

if __name__ == "__main__":
    reminder = Reminders()
    print reminder.is_reminder("Remind me to go there on Nov 2")
    print reminder.extract_date_time()
    while(True):
        ip = raw_input("Enter here:")
        print reminder.is_reminder(ip)
        reminder.extract_date_time()




