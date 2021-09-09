import krakenapi

class KrakenReportCreation:

    def create_report(self):
        k = krakenapi.API()
        k.load_key('kraken.key')
        req_data = {'report': 'ledgers', 'description': 'Automated Report'}
        json_output = k.query_private('AddExport',req_data)
        return json_output