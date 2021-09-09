import urllib.request, json
from datetime import date
from datetime import datetime, timedelta, date
import logging
import config

class krakenpriceapi:

    def __init__(self):
        logging.basicConfig(level=config.LOG_LEVEL)



    def get_close_price_list(self, req_date_time,pair_url_code,pair_json_code):
        epoch_req_date = req_date_time.timestamp()
        logging.debug(datetime.fromtimestamp(epoch_req_date))
        url = "https://api.kraken.com/0/public/Trades?pair=%s&since=%s"%(pair_url_code,epoch_req_date)
        logging.debug(url)
        response = urllib.request.urlopen(url)

        data = json.loads(response.read())
        logging.debug(data['result'].keys())
        ds = data['result'][pair_json_code]
        return data['result'][pair_json_code]


    #VWAP of the x minutes before ~virtual~ market close
    def get_vwap_close_price(self, req_date_time,pair_url_code,pair_json_code):
        time_spread=15

        start_time = req_date_time - timedelta(minutes=time_spread)
        end_time = req_date_time + timedelta(minutes=time_spread)

        trade_count = self.count_trades( start_time,end_time,pair_url_code,pair_json_code)
        counter = 0
        while trade_count <10 and counter <= 24:
            time_spread = time_spread + 15
            start_time = req_date_time - timedelta(minutes=time_spread)
            end_time = req_date_time + timedelta(minutes=time_spread)
            trade_count = self.count_trades(start_time, end_time, pair_url_code, pair_json_code)
            counter = counter +1

        logging.debug("Interval: "+str(start_time)+" - "+str(end_time) + " - " + str(counter) +" increase(s)")
        logging.debug("Nb of trades: "+str(trade_count))
        if trade_count == 0:
            return 0

        else:
            prices_data_list = self.get_close_price_list(start_time, pair_url_code, pair_json_code)
            count = 0
            total_volume =0
            price = 0
            sum_pricexvolume = 0
            for price_data in prices_data_list:
                trade_time = datetime.fromtimestamp(price_data[2])

                if trade_time >= start_time and trade_time <=end_time:
                    #logging.debug("Selected Trade Time: " + str(trade_time))
                    count = count + 1
                    total_volume = total_volume + float(price_data[1])
                    #logging.debug( str(price_data[0]))
                    #logging.debug(str(price_data[1]))
                    #logging.debug(str(price_data[2]))
                    sum_pricexvolume = sum_pricexvolume + (float(price_data[0]) * float(price_data[1]))

            vwap = sum_pricexvolume/total_volume
            return vwap


    #FINISH VWAP CALCULATION

    def count_trades(self, start_time,end_time,pair_url_code,pair_json_code):
        prices_data_list = self.get_close_price_list(start_time, pair_url_code, pair_json_code)
        count = 0
        for price_data in prices_data_list:
            trade_time = datetime.fromtimestamp(price_data[2])
            if trade_time >= start_time and trade_time <= end_time:
                count = count+1
        return count







"""
logging.basicConfig(level=config.LOG_LEVEL)
price_api = krakenpriceapi()

date_time_str = '2021-02-05 16:15:00'
date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

url_code = 'xbtusd'
currency_code = 'XXBTZUSD'

url_code = 'manausd'
currency_code = 'MANAUSD'


logging.debug ("VWAP= " + str(price_api.get_vwap_close_price(date_time_obj,url_code,currency_code)))
"""