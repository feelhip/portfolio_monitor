import ledgerloader
from datetime import date
import krakenhistoricalprice
import getsqldata



ledgerLoader = ledgerloader.LedgerLoader()
ledger = ledgerLoader.getLedger('ledger_XDQK.zip')

date_list = ledger[0]
assets_list = ledger[1]
nominals_list= ledger[2]
getSqlData = getsqldata.getsqldata()
price_api = krakenhistoricalprice.krakenpriceapi()

usd_assets_values_list=[]
usd_portfolio_values_list=[]


for date_dt , nominals in zip(date_list, nominals_list):
    usd_assets_values = []
    usd_portfolio_value = 0
    for nominal, asset in zip(nominals, assets_list):
        asset_codes_tuple = getSqlData.get_histo_price_code(asset)
        rate = price_api.get_vwap_close_price(date_dt, asset_codes_tuple[0], asset_codes_tuple[1])
        usd_asset_value = rate * nominal
        usd_assets_values.append(usd_asset_value)
        usd_portfolio_value = usd_portfolio_value + usd_asset_value
    usd_portfolio_values_list.append(usd_portfolio_value)
    usd_assets_values_list.append(usd_assets_values)


print (date_list)
print (assets_list)
print (usd_assets_values_list)
print (nominals_list)
print (usd_portfolio_values_list)