import krakenapi
import json
from datetime import datetime

class LivePortfolioNominals:

    def __init__(self):
        self.last_req_time = datetime.now()
        self.req_nb = 0
        self.last_ptf_returned = {}


    def get_nominals(self):
        self.req_nb = self.req_nb +1
        req_time = datetime.now()

        if self.req_nb ==1:

            k = krakenapi.API()
            k.load_key('kraken.key')

            balanceJsonOutput = k.query_private('Balance')
            portfolio_dict = balanceJsonOutput['result']

            non_null_ptf = {}

            for asset in portfolio_dict.keys():
                asset_value = portfolio_dict[asset]
                if float(asset_value) != float(0):
                    non_null_ptf.update({asset: asset_value})

            self.last_req_time = datetime.now()
            self.last_ptf_returned = non_null_ptf
            return non_null_ptf


        else:
            current_req_time = req_time.timestamp()
            previous_req_time = self.last_req_time.timestamp()

            if req_time.timestamp() > self.last_req_time.timestamp()+ 60:
                k = krakenapi.API()
                k.load_key('kraken.key')

                balanceJsonOutput = k.query_private('Balance')
                portfolio_dict = balanceJsonOutput['result']

                non_null_ptf = {}

                for asset in portfolio_dict.keys():
                    asset_value = portfolio_dict[asset]
                    if float(asset_value) != float(0):
                        non_null_ptf.update({asset: asset_value})
                self.last_ptf_returned = non_null_ptf

                self.last_req_time = datetime.now()
                return non_null_ptf

            else:
                return self.last_ptf_returned





