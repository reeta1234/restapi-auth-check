from django.apps import AppConfig
import logging
logging.basicConfig(filename='errorlog.log',level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')

class BenefitAppConfig(AppConfig):
    name = 'benefitapp'
    verbose_name = 'Benefit'