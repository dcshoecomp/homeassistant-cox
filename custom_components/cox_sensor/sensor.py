import logging
from datetime import datetime
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle
import requests
import json

__version_ = '0.1.2'

REQUIREMENTS = ['requests']

CONF_USERNAME="username"
CONF_PASSWORD="password"

ICON = 'mdi:cloud-braces'

SCOPE = "openid%20internal" #okta-login.js from cox login page
HOST_NAME = "www.cox.com" #okta-login.js
REDIRECT_URI = "https://"+ HOST_NAME +"/authres/code" #okta-login.js
AJAX_URL = "https://"+ HOST_NAME +"/authres/getNonce?onsuccess=" #okta-login.js
BASE_URL = 'https://cci-res.okta.com/' #okta-login.js
CLIENT_ID = '0oa1iranfsovqR6MG0h8' #okta-login.js
ISSUER = 'https://cci-res.okta.com/oauth2/aus1iraniwjGQcoad0h8' #okta-login.js
ON_SUCCESS_URL = "https%3A%2F%2Fwww.cox.com%2Fresaccount%2Fhome.html" #okta-login.js
onSuccessUrl = ON_SUCCESS_URL
nonceURL="https://www.cox.com/authres/getNonce?onsuccess=https%3A%2F%2Fwww.cox.com%2Fresimyaccount%2Fhome.html"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=2)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    add_entities([
	  cox_sensor(username=username, password=password, getattribute="data_used", interval=SCAN_INTERVAL),
	  cox_sensor(username=username, password=password, getattribute="percentage_used", interval=SCAN_INTERVAL),  
	  cox_sensor(username=username, password=password, getattribute="remaining_days", interval=SCAN_INTERVAL),  
	  cox_sensor(username=username, password=password, getattribute="expected_usage", interval=SCAN_INTERVAL),  
	], True) 


class cox_sensor(Entity):
    def __init__(self, username, password, getattribute, interval):
        self._username = username
        self._password = password
        self._getattribute = getattribute
        self.update = Throttle(interval)(self._update)

    def _update(self):
        try:
            data = {
            "username": self._username,
            "password": self._password,
            "options": {
                "multiOptionalFactorEnroll": False,
                "warnBeforePasswordExpired": False
            }
            }
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            r = requests.Session()
            nonceVal=r.get(AJAX_URL + ON_SUCCESS_URL).text
            oktasession=r.post(BASE_URL + "/api/v1/authn", data=json.dumps(data), headers=headers, verify=False)
            sessionToken = oktasession.json()['sessionToken']
            url= ISSUER + '/v1/authorize?client_id=' + CLIENT_ID + '&nonce=' + nonceVal + '&redirect_uri=' + REDIRECT_URI + '&response_mode=query&response_type=code&sessionToken=' + sessionToken + '&state=https%253A%252F%252Fwww.cox.com%252Fwebapi%252Fcdncache%252Fcookieset%253Fresource%253Dhttps%253A%252F%252Fwww.cox.com%252Fresaccount%252Fhome.cox&scope=' + SCOPE
            oktasignin=r.get(url,allow_redirects=True, verify=False)
            r.get("https://www.cox.com/internet/mydatausage.cox", verify=False)
            datausage = r.get("https://www.cox.com/internet/ajaxDataUsageJSON.ajax", verify=False)
            datausagejson = datausage.json()
            #date that cox last updated account usage
            lastupdatedbycox = datetime.strptime(datausagejson['modemDetails'][0]['lastUpdatedDate'], '%m/%d/%y')
            #Total Data amount to be used example: 1024 GB
            dataplan = datausagejson['modemDetails'][0]['dataPlan'].replace("&#160;"," ")
            #Current Plan example: Cox High Speed Internet - Preferred150 Package
            services = datausagejson['modemDetails'][0]['services'].replace("&#160;"," ")
            #service_end attribute, returns month/day/year 
            serviceperiod = datausagejson['modemDetails'][0]['servicePeriod'].split('-')
            serviceend = datetime.strptime(serviceperiod[1], '%m/%d/%y')

            #Total Data Used in GB example: 500 GB
            if self._getattribute=="data_used":
                _state = datausagejson['modemDetails'][0]['dataUsed']['totalDataUsed'].replace("&#160;GB","")
                _units = 'GB'
            #remaining days in service plan
            if self._getattribute=="remaining_days":
                _state = abs((datetime.today() - serviceend).days)
                _units = 'days'
            #Total Percent Used in % example: 50
            if self._getattribute=="percentage_used":
                _state = datausagejson['modemDetails'][0]['dataUsed']['renderPercentage']
                _units = '%'
            if self._getattribute=="expected_usage":
                #serviceend = datetime.strptime('8/25/19', '%m/%d/%y') #testing
                #lastupdatedbycox = datetime.strptime('08/02/19', '%m/%d/%y') #testing
                if serviceend.month==1:
                    totaldays = (serviceend-serviceend.replace(month=12,year=serviceend.year-1)).days
                else:
                    totaldays = (serviceend-serviceend.replace(month=serviceend.month-1)).days
                _state = round((100/totaldays)*float(totaldays-((serviceend - lastupdatedbycox).days)), 2)
                #_state = round((100/float(13))*float(totaldays-((serviceend - lastupdatedbycox).days)), 2) #testing
                _units = 'GB'
            self._state = _state
            self._attributes = {}
            self._attributes['last_update'] = lastupdatedbycox.strftime('%m/%d/%y')
            self._attributes['data_plan'] = dataplan
            self._attributes['service_end'] = serviceend.strftime('%m/%d/%y')
            self._attributes['service']= services
            self._attributes['unit_of_measurement'] = _units

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
