import logging
import voluptuous as vol
import async_timeout

import homeassistant.helpers.config_validation as cv
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
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.warn(f'{DOMAIN}: sensor: async_setup_entry: {entry}')

    coordinator = await get_coordinator(hass)

    entities = [ErieLowSaltBinarySensor(coordinator)]

    async_add_entities(entities)


class ErieLowSaltBinarySensor(Entity):
    """Representation of a sensor."""    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.info_type = "low_salt"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'{DOMAIN}.{self.info_type}'

    @property
    def device_class(self):
        return "problem"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        status = self.coordinator.data
        if status != None and status["warnings"]:
            return status["warnings"][0]["description"].find("Salt") != -1
        return False        

