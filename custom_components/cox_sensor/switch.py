import logging
import requests
import json
import voluptuous as vol
from datetime import timedelta
from lxml import html

from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_RESOURCES, CONF_SCAN_INTERVAL
    )
import homeassistant.helpers.config_validation as cv

VERSION = '21.03.0'
REQUIREMENTS = ['requests']
_LOGGER = logging.getLogger(__name__)

CONF_USERNAME="username"
CONF_PASSWORD="password"

SCOPE = "openid%20internal" #okta-login.js from cox login page
HOST_NAME = "www.cox.com" #okta-login.js
REDIRECT_URI = "https://"+ HOST_NAME +"/authres/code" #okta-login.js
AJAX_URL = "https://"+ HOST_NAME +"/authres/getNonce?onsuccess=" #okta-login.js
BASE_URL = 'https://cci-res.okta.com/' #okta-login.js
CLIENT_ID = '0oa1iranfsovqR6MG0h8' #okta-login.js
ISSUER = 'https://cci-res.okta.com/oauth2/aus1jbzlxq0hRR6jG0h8' #okta-login.js
ON_SUCCESS_URL = "https%3A%2F%2Fwww.cox.com%2Fresaccount%2Fhome.html" #okta-login.js
onSuccessUrl = ON_SUCCESS_URL
nonceURL="https://www.cox.com/authres/getNonce?onsuccess=https%3A%2F%2Fwww.cox.com%2Fresimyaccount%2Fhome.html"

DEFAULT_PREFIX = 'cox'


SCAN_INTERVAL = timedelta(minutes=5)
# Name, onoffFunction, Checkfunction, checkNode
SWITCH_TYPES = {
    'reboot': [
        'Reboot Modem', 'reboot',
        '', ''],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_RESOURCES, default=['reboot']):
        vol.All(cv.ensure_list, [vol.In(SWITCH_TYPES)]),
})


def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Set up the cox switches."""
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    resources = config.get(CONF_RESOURCES)

    _LOGGER.debug("Cox: Setup Switches")

    args = [username, password]
    switches = []
    for kind in resources:
        switches.append(CoxSwitch(args, kind, scan_interval))

    add_entities_callback(switches)


class CoxSwitch(SwitchEntity):
    """Representation of a netgear enhanced switch."""

    def __init__(self, args, kind, scan_interval):
        """Initialize the netgear enhanced switch."""
        self._name = SWITCH_TYPES[kind][0]
        self.entity_id = f"switch.{DEFAULT_PREFIX}_{kind}"
        self._nfFunction = SWITCH_TYPES[kind][1]
        self._username = args[0]
        self._password = args[1]
        self._is_on = None
        self._icon = None
        self._scan_interval = scan_interval

        self.update()

    @property
    def should_poll(self):
        """Poll enabled for the cox switch."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def is_on(self):
        """Return true if switch is on."""
        _LOGGER.debug("Cox Switch: check if %s is on.", self._name)
        if self._nfFunction in ('reboot'):
            self._is_on = False

        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug("Cox Switch: Turning on %s", self._name)
        if self._nfFunction in ('reboot'):
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
                cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(r.cookies))
                nonceVal=r.get(AJAX_URL + ON_SUCCESS_URL).text
                oktasession=r.post(BASE_URL + "/api/v1/authn", data=json.dumps(data), headers=headers, verify=False,cookies=cookies)
                sessionToken=oktasession.json()['sessionToken']
                url= ISSUER + '/v1/authorize?client_id=' + CLIENT_ID + '&nonce=' + nonceVal + '&redirect_uri=' + REDIRECT_URI + '&response_mode=query&response_type=code&sessionToken=' + sessionToken + '&state=https%253A%252F%252Fwww.cox.com%252Fwebapi%252Fcdncache%252Fcookieset%253Fresource%253Dhttps%253A%252F%252Fwww.cox.com%252Fresaccount%252Fhome.cox&scope=' + SCOPE
                r.get(url,allow_redirects=True, verify=False,cookies=cookies)
                resetlanding = r.get("https://www.cox.com/resaccount/equipment.html?serviceName=internet", verify=False,cookies=cookies)
                resetlanding = html.fromstring(resetlanding.text)
                resetlandingmac = resetlanding.xpath("//span[@class='serial-number']/text()", smart_strings=False)[1].replace("MAC: ","")
                resetmac = r.get("https://www.cox.com/resaccount/support/internet-device-reset-landing.html?macAddress=" + resetlandingmac, verify=False,cookies=cookies)
                resetmac = html.fromstring(resetmac.text)
                csrf = resetmac.xpath("//input[@name='_csrf']/@value", smart_strings=False)[0]
                data = {
                    'macAddress': resetlandingmac,
                    'serviceName': "internet",
                    '_csrf': csrf,
                    'submit': "Begin reset"
                }
                r.post("https://www.cox.com/resaccount/support/internet-device-reset-landing.html",data=data, verify=False,cookies=cookies)
            except Exception as err:
                _LOGGER.debug(oktasession.text)
                _LOGGER.error(err)

        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Cox Switch: Turning off %s", self._name)

        self._is_on = False
        self.schedule_update_ha_state()

    def update(self):
        """Check if is on."""
        # https://goo.gl/Nvioub
        _LOGGER.debug("Cox Switch update function")

        self._is_on = False
        #do functions to check sensor attributes if on or off

        return self._is_on
