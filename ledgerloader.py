class LedgerLoader:



    def unzip_file(self,ledger_zip_path):
        import zipfile
        with zipfile.ZipFile(ledger_zip_path, 'r') as zip_ref:
            zip_ref.extractall('ledger')


    def get_daily_assets_nominal(self):
        import csv
        file_path = 'ledger/ledgers.csv'
        a_csv_file = open(file_path, "r")

        dict_reader = csv.DictReader(a_csv_file)

        #ordered_dict_from_csv = list(dict_reader)[0]

        ledger_list = list(dict_reader)

        unique_asset_list = []
        for ledger in ledger_list:
            asset = ledger['asset']
            if asset not in unique_asset_list:
                unique_asset_list.append(asset)

        from datetime import datetime, timedelta
        ledger_start_date = datetime(2100, 1, 1, 12, 00, 1, 123000)
        for ledger in ledger_list:
            start_date_str = ledger['time']
            start_date=datetime.strptime(start_date_str,'%Y-%m-%d %H:%M:%S')
            if start_date<ledger_start_date:
                ledger_start_date = start_date



        date_list=[]
        #yesterday_dt = (datetime.now() - timedelta(1)).replace(hour=0,minute=0,second=0,microsecond=0)
        today_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ledger_start_date = ledger_start_date.replace(hour=0,minute=0,second=0,microsecond=0)

        while ledger_start_date <= today_dt:
            date_list.append(ledger_start_date)
            ledger_start_date = ledger_start_date+ timedelta(1)

        day_counter = 0
        daily_balances_list=[]
        for selected_date in date_list:
            selected_day_balance_list=[]
            asset_counter = 0
            for selected_asset in unique_asset_list:
                asset_day_balance = []
                asset_day_balance_time = []
                for ledger_line in ledger_list:
                    ledger_time = datetime.strptime(ledger_line['time'],'%Y-%m-%d %H:%M:%S')
                    asset=ledger_line['asset']
                    open_date_time = selected_date
                    close_date_time = selected_date.replace(hour=23,minute=59,second=59,microsecond=999999)
                    if ledger_time>= open_date_time and ledger_time <= close_date_time and selected_asset == asset:
                        if ledger_line['balance'] == '':
                            asset_day_balance.append(0)
                        else:
                            asset_day_balance.append(ledger_line['balance'])
                        asset_day_balance_time.append(ledger_line['time'])
                sz = len(asset_day_balance)
                if sz == 0: # balance was not updated that day
                    if day_counter >0: # we are not on the first day of the portfolio creation
                        previous_day_balance = daily_balances_list[day_counter-1][asset_counter]
                        selected_day_balance_list.append(previous_day_balance)  # append the balance of the previous day
                    else:
                        selected_day_balance_list.append(0)
                else:
                    latest_update_date = asset_day_balance_time[0]
                    latest_update_balance = asset_day_balance[0]
                    for sel_balance, sel_date in zip(asset_day_balance,asset_day_balance_time):
                        sel_date_dt = datetime.strptime(sel_date,'%Y-%m-%d %H:%M:%S')
                        latest_update_date_dt = datetime.strptime(latest_update_date,'%Y-%m-%d %H:%M:%S')
                        if sel_date_dt > latest_update_date_dt:
                            latest_update_balance = sel_balance
                    selected_day_balance_list.append(float(latest_update_balance))
                asset_counter = asset_counter +1
            day_counter = day_counter + 1
            daily_balances_list.append(selected_day_balance_list)
        return date_list, unique_asset_list,daily_balances_list





    def getLedger(self,zip_file_path):
        self.unzip_file(zip_file_path)
        return self.get_daily_assets_nominal()
















