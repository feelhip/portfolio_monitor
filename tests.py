import datetime
import krakenhistoricalprice
import krakenapi
import krakenreportdownload
import ledgerloader

k = krakenapi.API()
k.load_key('kraken.key')
req_data = {'report': 'ledgers','description':'Automated Report'}
#ledgerJsonOutput = k.query_private('AddExport',req_data)
#print (ledgerJsonOutput)


#{'error': [], 'result': {'id': 'WHWP'}}


"""
req_data = {'id': 'WHWP'}
ledgerJsonOutput = k.query_private('RetrieveExport',req_data)

f = open("ledger_content.txt", "a")
f.write(ledgerJsonOutput)
f.close()



print (ledgerJsonOutput)

"""


reportDownload = krakenreportdownload.KrakenReportDownload()

reportDownload.download_report("QBFU")

