"""
"""
import logging
import requests

import voluptuous as vol
from datetime import timedelta

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_RESOURCES, CONF_SCAN_INTERVAL
    )
import homeassistant.helpers.config_validation as cv

VERSION = '0.0.1'
REQUIREMENTS = ['requests']
_LOGGER = logging.getLogger(__name__)

CONF_USERNAME="username"
CONF_PASSWORD="password"

url="https://idm.east.cox.net/idm/coxnetlogin"

DEFAULT_PREFIX = 'cox'


SCAN_INTERVAL = timedelta(minutes=5)
# Name, onoffFunction, Checkfunction, checkNode
SWITCH_TYPES = {
    'reboot': [
        'Reboot Router', 'reboot',
        '', ''],
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({

    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_RESOURCES, default=['reboot']):
        vol.All(cv.ensure_list, [vol.In(SWITCH_TYPES)]),
})


def setup_platform(hass, config, add_entities_callback, discovery_info=None):
    """Set up the netgear_enhanced switches."""
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    scan_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    resources = config[CONF_RESOURCES]

    _LOGGER.debug("Cox: Setup Switches")

    args = [password, username]
    switches = []
    for kind in resources:
        switches.append(CoxSwitch(
            args, kind, scan_interval)
        )

    add_entities_callback(switches)


class CoxSwitch(SwitchDevice):
    """Representation of a netgear enhanced switch."""

    def __init__(self, args, kind, scan_interval):
        """Initialize the netgear enhanced switch."""
        self._name = SWITCH_TYPES[kind][0]
        self.entity_id = f"switch.{DEFAULT_PREFIX}_{kind}"
        self._nfFunction = SWITCH_TYPES[kind][1]
        self._username = SWITCH_TYPES[kind][1]
        self._password = SWITCH_TYPES[kind][0]
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
                r.get("https://www.cox.com/resaccount/refresh-modem.cox")
                r.get("https://www.cox.com/resaccount/refresh-modem.cox/ajaxModemReset.ajax?option=hit", verify=False)
            except Exception as err:
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
