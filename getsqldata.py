import sqlite3
import config
import logging
import sys

class getsqldata:

    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):

        conn = None
        try:
            conn = sqlite3.connect(config.DB_LOCATION)
        except Exception as e:
            logging.error(e)

        return conn




    def get_histo_price_code(self,ledger_ccy_code):
        request = """SELECT to_usd_url_code,to_usd_json_code FROM histo_price_codes WHERE ledger_ccy_code = \'%s\'"""%(ledger_ccy_code)
        logging.debug(request)
        cursor = self.connection.execute(request)
        return cursor.fetchone()


    def get_live_json_codes_dict(self):
        codes_dict ={}
        request = """SELECT ledger_ccy_code, ws_to_usd_json_code FROM histo_price_codes """
        logging.debug(request)
        cursor = self.connection.execute(request)
        sql_output =cursor.fetchall()

        for output in sql_output:
            codes_dict[output[0]]=output[1]

        return codes_dict






