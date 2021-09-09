#!/usr/bin/env python

# This file is part of krakenex.
# Licensed under the Simplified BSD license. See `examples/LICENSE.txt`.

# Prints the account blance to standard output.

import krakenapi
import json
import logging
import datetime
from datetime import date
import krakenhistoricalprice
import getsqldata
import config

class KrakenLedger:


    def __init__(self):
        k = krakenapi.API()
        k.load_key('kraken.key')
        req_data = {'type': 'all'}
        self.ledgerJsonOutput = k.query_private('Ledgers',req_data)
        logging.debug("Complete Ledger:")
        logging.debug(self.ledgerJsonOutput)
        self.current_balance = k.query_private('Balance')
        self.getSqlData = getsqldata.getsqldata()


    def get_today_assets_nominal(self):



        ledger = self.ledgerJsonOutput['result']['ledger']

        unique_asset_list = []
        for data in ledger.items():
            asset = data[1]['asset']
            if  asset not in unique_asset_list:
                unique_asset_list.append( asset)

        unique_amount_list=[]
        for asset in unique_asset_list:
            unique_amount = float(0)
            for ledger_line in ledger.items():
                #print (ledger_line[1]['asset'] +" "+ ledger_line[1]['amount'] +" "+ ledger_line[1]['type'] +" "+ str(ledger_line[1]['time'])) #ex: refid': 'STIQAGI-JJDBJ-PHVWRA', 'time': 1612513526.7026, 'type': 'staking', 'subtype': '', 'aclass': 'currency', 'asset': 'DOT.S', 'amount': '0.0039719200', 'fee': '0.0000000000', 'balance': '4.0342767000
                if asset == ledger_line[1]['asset']:
                    unique_amount = unique_amount + float(ledger_line[1]['amount'])
            unique_amount_list.append(unique_amount)

        for y in range (0,len(unique_asset_list)):
            logging.debug(unique_asset_list[y])
            logging.debug(unique_amount_list[y])


        return unique_asset_list, unique_amount_list


    def get_assets_nominal(self,req_date):
        import datetime as dt
        ledger = self.ledgerJsonOutput['result']['ledger']
        logging.debug(ledger)

        unique_asset_list = []
        for data in ledger.items():
            asset = data[1]['asset']
            if  asset not in unique_asset_list:
                unique_asset_list.append( asset)

        unique_amount_list=[]
        for asset in unique_asset_list:
            unique_amount = float(0)
            for ledger_line in ledger.items():
                #print (ledger_line[1]['asset'] +" "+ ledger_line[1]['amount'] +" "+ ledger_line[1]['type'] +" "+ str(ledger_line[1]['time'])) #ex: refid': 'STIQAGI-JJDBJ-PHVWRA', 'time': 1612513526.7026, 'type': 'staking', 'subtype': '', 'aclass': 'currency', 'asset': 'DOT.S', 'amount': '0.0039719200', 'fee': '0.0000000000', 'balance': '4.0342767000
                ledger_time = ledger_line[1]['time']
                checked_time = dt.datetime.combine(req_date, dt.datetime.min.time()).timestamp()+86399

                logging.debug("Ledger ID checked: "+str(ledger_line[0]))
                logging.debug("Ledger timestamp = " + str(datetime.datetime.fromtimestamp(ledger_time)))
                logging.debug("Checked timestamp = " + str(datetime.datetime.fromtimestamp(checked_time)))


                if asset == ledger_line[1]['asset'] and (ledger_time) <= ( checked_time):
                # if asset == ledger_line[1]['asset'] and  datetime.date.fromtimestamp(ledger_line[1]['time']-18000)<=req_date:

                    logging.debug('Ledger line recorded')
                    unique_amount = unique_amount + float(ledger_line[1]['amount'])
                else : logging.debug('Ledger line ignored')
            unique_amount_list.append(unique_amount)

        for y in range (0,len(unique_asset_list)):
            logging.debug(unique_asset_list[y])
            logging.debug(unique_amount_list[y])


        return unique_asset_list, unique_amount_list



    def get_histo_daily_assets_nominal(self):
        #first_transaction_epoch_date = self.get_first_transaction_epoch_date()
        origin_date = datetime.date.fromtimestamp(self.get_first_transaction_epoch_date())
        end_date = date.today()
        delta = datetime.timedelta(days=1)
        dates_list = []
        assets_amounts_list =[]

        while origin_date <= end_date:
            logging.debug(origin_date)
            dates_list.append(origin_date)
            assets_amounts_list.append(self.get_assets_nominal(origin_date))
            origin_date += delta

        return dates_list,assets_amounts_list







    def get_first_transaction_epoch_date(self):
        ledger = self.ledgerJsonOutput['result']['ledger']
        first_transaction_date_epoch = 2556105635 #some date in 2050
        for data in ledger.items():
            transaction_date_epoch = data[1]['time']
            if  first_transaction_date_epoch > transaction_date_epoch:
                first_transaction_date_epoch = transaction_date_epoch
        return first_transaction_date_epoch




    def get_histo_daily_assets_usd_value(self):
        days = krakenLedger.get_histo_daily_assets_nominal()[0]
        all_assets_nominals = krakenLedger.get_histo_daily_assets_nominal()[1]
        price_api = krakenhistoricalprice.krakenpriceapi()
        all_usd_assets_value = []
        daily_portfolio_usd_value=[]
        for day, day_assets_nominal in zip(days, all_assets_nominals):
            portfolio_usd_value = 0
            day_usd_assets_value = []
            for asset,nominal in zip(day_assets_nominal[0],day_assets_nominal[1]):
                day_dt = datetime.datetime.combine(day, datetime.datetime.min.time())
                asset_codes_tuple = self.getSqlData.get_histo_price_code(asset)
                rate = price_api.get_vwap_close_price(day_dt,asset_codes_tuple[0],asset_codes_tuple[1])
                asset_nominal_usd_value = rate*nominal
                day_usd_assets_value.append(asset_nominal_usd_value)
                portfolio_usd_value = portfolio_usd_value +asset_nominal_usd_value
            all_usd_assets_value.append(day_usd_assets_value)
            daily_portfolio_usd_value.append(portfolio_usd_value)
        return days,all_assets_nominals,all_usd_assets_value,daily_portfolio_usd_value




krakenLedger = KrakenLedger()

print(krakenLedger.get_assets_nominal(datetime.date(2021, 1, 8)))

"""
logging.basicConfig(level=config.LOG_LEVEL)

krakenLedger = KrakenLedger()
krakenLedger.get_today_assets_nominal()

logging.debug(krakenLedger.get_first_transaction_epoch_date())

krakenLedger.get_histo_daily_assets_nominal()

full_ledger =  krakenLedger.get_histo_daily_assets_usd_value()

days = full_ledger[0]
assets_amounts = full_ledger[1]
assets_values = full_ledger[2]
daily_portfolio_value =full_ledger[3]

logging.info(days)
logging.info(assets_amounts)
logging.info(assets_values)
logging.info(daily_portfolio_value)


logging.debug("end")
"""