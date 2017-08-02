import os
import json
from sutime import SUTime

if __name__ == '__main__':
    test_case = u'I need a desk for tomorrow from 2pm to 3pm'

    jar_files = "/home/urjit/del_this/jars"
    sutime = SUTime(jars=jar_files, mark_time_ranges=False)

    print(json.dumps(sutime.parse(test_case), indent=4))

    while(True):
        text = raw_input("Enter here: ")

        times = sutime.parse(text)
        if len(times) > 0:
            for time in times:
                type=time['type']
                val=time['value']
                print type
                print val




#
# import nltk
#
# tagged = nltk.pos_tag("Hi, reminnd me at 8".split())
# print tagged