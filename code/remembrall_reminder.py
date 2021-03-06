import os
import re
import json

from decimal import Decimal
from natty import DateParser
from datetime import datetime, timedelta
from remembrall_db_helper import PostgresHelper
import remembrall_util
import pytz
from pytz import timezone


config_dict = remembrall_util.get_configs()
class Reminders(object):
    def __init__(self):
        self.date_result = None
        self.day = ""
        self.month = ""
        self.year = ""
        self.hour = ""
        self.min = ""
        self.message_text = ""
        self.msg_id = ""

    def is_reminder(self, text):
        result = DateParser(text).result()
        print result
        if result is not None and len(result) > 0:
            self.date_result = result[0].astimezone(timezone('UTC'))
            print self.date_result
            self.message_text = text
            print self.date_result
            return True
        return False

    def extract_date_time(self, offset):
        try:
            print self.message_text
            result = DateParser(self.message_text).result()
            self.date_result = result[0].astimezone(tz=pytz._FixedOffset((offset*60)))
            if " in " in self.message_text or " after " in self.message_text:
                offset = 0
            print "before", self.date_result
            print "offset", offset
            self.date_result -= timedelta(hours=offset)
            print "after", self.date_result
            self.year = self.date_result.year
            self.month = self.date_result.month
            self.day = self.date_result.day
            self.hour = self.date_result.hour
            self.min = self.date_result.minute
        except Exception as e:
            print str(e)

    def update_reminder_table(self, usr_id, msg_id):
        print "In here: "
        reminder_dict = {}
        try:
            reminder_dict = {'usr_id':  usr_id
                            ,'msg_id': msg_id
                            ,'msg_text': self.message_text
                            ,'year': self.year
                            ,'month': self.month
                            ,'date': self.day
                            ,'hh': self.hour
                            ,'mm': self.min
                            ,'sent': "F"
                            ,'crt_ts': str(datetime.now())
                            ,'upd_ts': str(datetime.now()) }
            print reminder_dict
        except Exception as e:
            print str(e)
        postgres = PostgresHelper()
        print "Updating table: ", reminder_dict
        postgres.postgres_insert_dictionary_list(table_name=config_dict['REMINDER_TABLE'],
                                                 dict_list=[reminder_dict])



if __name__ == "__main__":
    reminder = Reminders()
    #print reminder.is_reminder("Remind me to go there on Nov 2")
    #print reminder.year
    while(True):
        ip = raw_input("Enter here:")

        print reminder.is_reminder(ip)
        d = float(Decimal('-7'))
        print d
        reminder.extract_date_time(offset=d)
        print reminder.date_result
        print "Y:", reminder.year, "M:", reminder.month, "D:", reminder.day, "H:", reminder.hour, "M:", reminder.min




