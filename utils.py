import datetime
import logging
import config

class Utils:
    def is_same_day(self,date_epoch1, date_epoch2):
        datetime_epoch1 = datetime.datetime.fromtimestamp(date_epoch1)
        datetime_epoch2 = datetime.datetime.fromtimestamp(date_epoch2)
        if datetime_epoch1.date() == datetime_epoch2.date():
            return True
        else:
            return False


utils = Utils()

logging.basicConfig(level=config.LOG_LEVEL)

date1 = 1610114171.0762
date2 = 1610114171.0762

logging.debug(utils.is_same_day(date1,date2))