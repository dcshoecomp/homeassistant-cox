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
	  cox_sensor(username=username, password=password, getattribute="totalDataUsed", interval=SCAN_INTERVAL),
	  cox_sensor(username=username, password=password, getattribute="actualPercentage", interval=SCAN_INTERVAL),  
	  cox_sensor(username=username, password=password, getattribute="services", interval=SCAN_INTERVAL),
	  cox_sensor(username=username, password=password, getattribute="dataPlan", interval=SCAN_INTERVAL),
	  cox_sensor(username=username, password=password, getattribute="servicePeriod", interval=SCAN_INTERVAL) 
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
			
            #Total Data Used in GB example: 500 GB
            if self._getattribute=="totalDataUsed":
              currentusage = (datausage.json())['modemDetails'][0]['dataUsed']['totalDataUsed'].replace("&#160;"," ")
			
            #Total Percent Used in % example: 50
            if self._getattribute=="actualPercentage":
              currentusage = (datausage.json())['modemDetails'][0]['dataUsed']['renderPercentage']
			
            #Current Plan example: Cox High Speed Internet - Preferred150 Package
            if self._getattribute=="services":
              currentusage = (datausage.json())['modemDetails'][0]['services'].replace("&#160;"," ")
			
            #Total Data amount to be used example: 1024 GB
            if self._getattribute=="dataPlan":
              currentusage = (datausage.json())['modemDetails'][0]['dataPlan'].replace("&#160;"," ")
			
            #Service Period example: 06/25/19-07/24/19
            if self._getattribute=="servicePeriod":
              currentusage = (datausage.json())['modemDetails'][0]['servicePeriod']
						
            self._state = currentusage
            self._attributes = {}
            self._attributes['last_update'] = datetime.now()
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

