import datetime

from remembrall_db_helper import PostgresHelper

import remembrall_util
import urllib2
import json


config_dict = remembrall_util.get_configs()

class UserTableManager(object):

    def __init__(self):
        self.usr_ids_to_fetch = set()
        self.profiles_to_insert = list()

    def update_profiles(self):
        postgres = PostgresHelper()
        print "Printing profiles:", self.profiles_to_insert
        postgres.postgres_insert_dictionary_list(table_name=config_dict['USR_TABLE'], dict_list=self.profiles_to_insert)


    def get_ids_from_log(self):
        postgres = PostgresHelper()

        cmd = 'SELECT distinct A.usr_id from {} A ' \
              'left outer join {} B ' \
              'on A.usr_id = B.usr_id ' \
              'where B.usr_id is NULL'.format(config_dict['LOG_TABLE'], config_dict['USR_TABLE'])

        usr_ids = postgres.postgres_executor(cmd, return_dict=True)

        for dd in usr_ids:
            self.usr_ids_to_fetch.add(dd['usr_id'])

    def get_user_profile_info(self, usr_id):
        if usr_id is None or usr_id.strip() == "":
            return None
        try:
            url = "https://graph.facebook.com/v2.6/{}?fields=first_name,last_name,timezone&access_token={}".format(usr_id, config_dict['PAGE_ACCESS_TOKEN'])
            print url
            print len(self.profiles_to_insert)
            print usr_id
            response = urllib2.urlopen(url)
            data = json.load(response)
            return data
        except Exception as err:
            print "Error for: ", usr_id
            print err
            print "Error while calling Facebook API"
            print "Skipping"

    def full_table_process(self):
        self.get_ids_from_log()

        for usr_id in self.usr_ids_to_fetch:
            if usr_id == 'urjit':
                continue
            profile = self.get_user_profile_info(usr_id=usr_id)
            if profile is None:
                continue
            profile['usr_id'] = usr_id
            profile['cr_ts'] = str(datetime.datetime.now())
            self.profiles_to_insert.append(profile)

        self.update_profiles()

    def process(self, usr_id):
        profile = self.get_user_profile_info(usr_id=usr_id)
        profile['usr_id'] = usr_id
        profile['cr_ts'] = str(datetime.datetime.now())
        self.profiles_to_insert.append(profile)

        self.update_profiles()

    def profile_exists(self, usr_id):
        postgres = PostgresHelper()
        results = postgres.postgres_select(table_name=config_dict['USR_TABLE'], condition=" WHERE usr_id=%s",
                                           parameters=[usr_id], return_dict=True)
        print results
        if results is not None and len(results) > 0:
            return True
        return False

    def get_usr_timezone(self, usr_id):

        postgres = PostgresHelper()
        results = postgres.postgres_select(table_name=config_dict['USR_TABLE'], condition=" WHERE usr_id=%s",
                                           parameters=[usr_id], req_column_list=['timezone'], return_dict=True)
        print "results" , results
        try:
            return results[0]['timezone']
        except:
            print "Could not fetch timezone"
            return 0

if __name__ == '__main__':
    userTableManager = UserTableManager()
    userTableManager.full_table_process()







