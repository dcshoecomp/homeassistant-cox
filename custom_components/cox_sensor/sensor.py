import logging

from datetime import timedelta
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle

REQUIREMENTS = ['requests']

CONF_USERNAME="username"
CONF_PASSWORD="password"

ICON = 'mdi:cloud-braces'

url="https://idm.east.cox.net/idm/coxnetlogin"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    add_entities([
	  cox_sensor(username=username, password=password, getattribute="data_used", interval=SCAN_INTERVAL),
	  cox_sensor(username=username, password=password, getattribute="percentage_used", interval=SCAN_INTERVAL),  
	  cox_sensor(username=username, password=password, getattribute="remaining_days", interval=SCAN_INTERVAL),  
	], True) 


class cox_sensor(Entity):
    def __init__(self, username, password, getattribute, interval):
        self._username = username
        self._password = password
        self._getattribute = getattribute
        self.update = Throttle(interval)(self._update)

    def _update(self):
        import requests
        try:
            data= {
            'username': self._username,
            'password': self._password,
            'rememberme': 'true',
            'emaildomain': '@cox.net',
            'targetFN': 'COX.net',
            'onsuccess': 'https://www.cox.com/resaccount/home.cox',
            'post': 'Submit'
            }
            r = requests.Session()
            r.post(url, data=data, verify=False)
            r.get("https://www.cox.com/internet/mydatausage.cox")
            datausage = r.get("https://www.cox.com/internet/ajaxDataUsageJSON.ajax", verify=False)
            datausagejson = datausage.json()
            #date that cox last updated account usage
            lastupdatedbycox = datausagejson['modemDetails'][0]['lastUpdatedDate']
            #Total Data amount to be used example: 1024 GB
            dataplan = datausagejson['modemDetails'][0]['dataPlan'].replace("&#160;"," ")
            #remaining days in service plan
            #Current Plan example: Cox High Speed Internet - Preferred150 Package
            services = datausagejson['modemDetails'][0]['services'].replace("&#160;"," ")

            #Total Data Used in GB example: 500 GB
            if self._getattribute=="data_used":
              _state = datausagejson['modemDetails'][0]['dataUsed']['totalDataUsed'].replace("&#160;"," ")
            #Total Percent Used in % example: 50
            if self._getattribute=="remaining_days":
                serviceperiod = datausagejson['modemDetails'][0]['servicePeriod'].split('-')
                serviceend = datetime.strptime(serviceperiod[1], '%m/%d/%y')
                _state = abs((datetime.today() - serviceend).days)
            if self._getattribute=="percentage_used":
              _state = datausagejson['modemDetails'][0]['dataUsed']['renderPercentage']
            
            self._state = _state
            self._attributes = {}
            self._attributes['last_update'] = lastupdatedbycox
            self._attributes['data_plan'] = dataplan
            self._attributes['service_end'] = serviceend.strftime('%m/%d/%y')
            self._attributes['service']= services

        except Exception as err:
            _LOGGER.error(err)


    @property
    def name(self):
        name = "cox_sensor_" +  self._getattribute
        return name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def should_poll(self):
        """Return the polling requirement for this sensor."""
        return True
