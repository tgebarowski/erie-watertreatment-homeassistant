import logging
import voluptuous as vol
import async_timeout

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.const import CONF_HOST, CONF_ACCESS_TOKEN, CONF_USERNAME

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
)
from homeassistant import exceptions
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from datetime import timedelta
from erie_connect.client import ErieConnect
from . import get_coordinator


from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_UID,
    CONF_EXPIRY,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.warn(f'{DOMAIN}: sensor: async_setup_entry: {entry}')

    coordinator = await get_coordinator(hass)

    entities = [ErieVolumeIncreaseSensor(hass, coordinator, "total_volume", "flow", "L"),
                ErieStatusSensor(coordinator, "last_regeneration", ""),
                ErieStatusSensor(coordinator, "nr_regenerations", ""),
                ErieStatusSensor(coordinator, "last_maintenance", ""),
                ErieStatusSensor(coordinator, "total_volume", "L"),
                ErieWarning(coordinator)]

    async_add_entities(entities)

class ErieVolumeIncreaseSensor(Entity):

    def __init__(self, hass, coordinator, info_type, sensor_name, unit):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self.info_type = info_type
        self.sensor_name = sensor_name
        self.unit = unit

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'{DOMAIN}.{self.sensor_name}'

    @property
    def state(self):
        """Return the state of the sensor."""
        sensor_name = f'sensor.{DOMAIN}_{self.info_type}'
        old_state = self.hass.states.get(f'{sensor_name}')
        _LOGGER.warn(f'{sensor_name}: sensor: state: {self.coordinator.data} old_state: {old_state}')
        if self.coordinator.data != None and self.info_type in self.coordinator.data and old_state != None:
            old_value = self.get_int_from_sensor_value(old_state.state)
            new_value = self.get_int_from_sensor_value(self.coordinator.data[self.info_type])
            flow = new_value - old_value
        else:
            flow = 0
        return flow

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.unit

    def get_int_from_sensor_value(self, string_value):
        if string_value != None:
            return int(string_value.split()[0])
        return None

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()

class ErieWarning(Entity):
    """Representation of a sensor."""    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.info_type = "warnings"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'{DOMAIN}.{self.info_type}'

    @property
    def state(self):
        """Return the state of the sensor."""

        _LOGGER.warn(f'{DOMAIN}: sensor: state: {self.coordinator.data}')
        status = self.coordinator.data
        if status != None:
            warning_string = ""
            for warning in status[self.info_type]:
                warning_string += "⚠️ " + warning["description"] + "\n"
            return warning_string if warning_string != "" else None
        return None

class ErieStatusSensor(Entity):
    """Representation of a sensor."""    
    def __init__(self, coordinator, info_type, unit):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.info_type = info_type
        self.unit = unit

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'{DOMAIN}.{self.info_type}'

    @property
    def state(self):
        """Return the state of the sensor."""

        _LOGGER.warn(f'{DOMAIN}: sensor: state: {self.coordinator.data}')
        status = self.coordinator.data
        if status != None:
            return status[self.info_type]
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self.unit


