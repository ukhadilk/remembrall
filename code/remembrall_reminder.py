import os
import json
from sutime import SUTime
import remembrall_util

config_dict = remembrall_util.get_configs()

class Reminders(object):
    def __init__(self):
        self.jar_files = os.path.join(config_dict['PARENT_DIR'], config_dict['su_jars_path'])
        self.sutime = SUTime(jars=self.jar_files, mark_time_ranges=False)
        self.curr_time    = []
        self.curr_type = ""
        self.curr_val = ""
        self.reminder_date = "" #yyyy-mm-dd
        self.reminder_time = "" ##hh:mm (24 hour clock)

    def is_reminder(self, tokens):
        self.curr_times = []
        times = json.dumps(self.sutime.parse(tokens), indent=4)
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
        if self.curr_type == "DATE":
            self.reminder_date = self.curr_val


