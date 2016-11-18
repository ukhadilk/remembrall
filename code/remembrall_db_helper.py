import psycopg2 as psycopg2
import psycopg2.extras
import logging as log

log.basicConfig(level=log.INFO)

import remembrall_util
config_dict = remembrall_util.get_configs()

class PostgresHelper(object):
    """Database Connector Class"""

    def __init__(self):
        attempt_number = 1
        while (True):
            try:
                #TODO: CHANGE TO CONNECTION STRING FROM CONFIG FILE
                self.con = psycopg2.connect("dbname=postgres user=postgres password=urjit@123 host=localhost")
                break
            except Exception as err:
                try:
                    log.error("Postgres error [{}]: {}".format(err.args[0],
                                                               err.args[1]))
                except IndexError:
                    log.error("Postgres Error: {}".format(str(err)))
                attempt_number += 1
                #TODO: this should come from configurations
                if attempt_number <= 3:
                    log.error("Error in connecting to Database. Attempt to %d", attempt_number)
                else:
                    log.error("Failed to connect to database %d times", attempt_number-1)
                    log.info("Exiting")
                    #TODO: HANDLE THIS
                    raise SystemExit

    def postgres_insert_dictionary_list(self, table_name, dict_list):
        if table_name == "" or table_name is None:
            log.error("Table name not specified")
            raise ValueError("Table name not specified")
        if type(dict_list) is not list:
            raise TypeError("parameters to postgres_insert_dictionary_list should be a list")

        try:
            log.debug("Inserting")
            cur_insert_dict = self.con.cursor()
            for record_dict in dict_list:
                insert_dict_command = "INSERT INTO {} ({}) VALUES ({})".format \
                    (table_name, ', '.join('{}'.format(k) \
                                            for k in record_dict), ', '.join(
                        '{}'.format('%s') for k in record_dict))
                try:
                    cur_insert_dict.execute(insert_dict_command, record_dict.values())
                except Exception as err:
                    print 'Exception table: ', table_name, ', sql: ', insert_dict_command, record_dict.values()
                    print err
                    try:
                        log.error("Error in insertion command")

                        log.error("Postgres error [{}]: {}".format(err.args[0],
                                                           err.args[1]))
                    except IndexError:
                        log.error("Postgres Error: {}".format(str(err)))
                    raise SystemExit
            self.con.commit()
            cur_insert_dict.close()

        except Exception as err:
            try:
                log.error("Postgres error [{}]: {}".format(err.args[0],
                                               err.args[1]))
            except IndexError:
                log.error("Postgres Error: {}".format(str(err)))
                raise SystemExit

    def postgres_select(self, table_name, req_column_list='*', return_dict=False,
                        condition="", parameters=[]):
        """

        :rtype: list"""
        if table_name == "" or table_name is None:
            log.error("Table name not specified")
            raise ValueError("Table name not specified")
        if type(parameters) is not list:
            raise TypeError("parameters to postgres_select should be a list")

        #TODO: CHECK IF REQUIRED COLUMN LIST IS A LIST
        try:
            if return_dict:
                cur_select = self.con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cur_select = self.con.cursor()

            select_command = "SELECT {} FROM {} {} ".format(', '.join( \
                '{}'.format(col) for col in req_column_list),\
                table_name,condition)

            try:
                cur_select.execute(select_command, parameters)
                fetched_rows = []
                for row in cur_select:
                    fetched_rows.append(row)
                cur_select.close()
                return fetched_rows
            except Exception as err:
                try:
                    log.error("Error in select command")

                    log.error("Postgres error [{}]: {}".format(err.args[0],
                                                       err.args[1]))
                except IndexError:
                    log.error("Postgres Error: {}".format(str(err)))

        except Exception as err:
            try:
                log.error("Error in select command")

                log.error("Postgres error [{}]: {}".format(err.args[0],
                                                   err.args[1]))
            except IndexError:
                log.error("Postgres Error: {}".format(str(err)))
            raise SystemExit
        cur_select.close()

    def postgres_select_max_from(self, table_name, column_name):
        if table_name == "" or table_name is None:
            log.error("Table name not specified")
            raise ValueError("Table name not specified")

        if column_name == "" or column_name is None:
            log.error("column_name not specified")
            raise ValueError("column_name not specified")

        select_max_command = ""
        try:
            returned_max_value = None
            cur_select_max = self.con.cursor()
            select_max_command = "SELECT MAX({}) FROM {}".format(column_name, table_name)
            cur_select_max.execute(select_max_command)

            for row in cur_select_max:
                returned_str  =row[0]
                if returned_str is None or returned_str == "":
                    log.warning("No max value returned. Table might be empty")
                    log.warning("assigning returned max value 0")
                    returned_max_value = 0
                else:
                    returned_max_value = int(returned_str)
                cur_select_max.close()
                return returned_max_value
        except Exception, err:
            print 'Exception table:', table_name, ', sql: ', select_max_command
            print err
            try:
                log.error("Error in select command")

                log.error("Postgres error [{}]: {}".format(err.args[0],
                                                   err.args[1]))
            except IndexError:
                log.error("Postgres Error: {}".format(str(err)))
            raise SystemExit


