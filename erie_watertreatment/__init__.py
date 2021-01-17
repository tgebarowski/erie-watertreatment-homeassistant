"""Erie IQ26 Water Treatment integration"""

import logging
import voluptuous as vol
import async_timeout

from datetime import timedelta

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.const import CONF_HOST, CONF_ACCESS_TOKEN, CONF_USERNAME

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant import exceptions

from erie_connect.client import ErieConnect

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, entity_registry, update_coordinator


from .const import (
    DOMAIN,
    COORDINATOR,
    API,
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

PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [CONFIG_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    _LOGGER.warn(f'{DOMAIN}: async_setup')

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    _LOGGER.warn(f'{DOMAIN}: async_setup_entry: entry {entry} ')

    api = ErieConnect(entry.data[CONF_EMAIL],
                      entry.data[CONF_PASSWORD],
                      ErieConnect.Auth(entry.data[CONF_ACCESS_TOKEN],
                                       entry.data[CONF_CLIENT_ID],
                                       entry.data[CONF_UID],
                                       entry.data[CONF_EXPIRY]),
                      ErieConnect.Device(entry.data[CONF_DEVICE_ID],
                                         entry.data[CONF_DEVICE_NAME]))
    # Make sure coordinator is initialized.
    await create_coordinator(hass, api)
    
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
        
    return True
    

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    return unload_ok

async def get_coordinator(hass):
    return hass.data[DOMAIN]

async def create_coordinator(hass, api):
    """Get the data update coordinator."""
    if DOMAIN in hass.data:
        return hass.data[DOMAIN]

    async def async_fetch_info():
        """Fetch data from API endpoint.
        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with async_timeout.timeout(120):
                response = await hass.async_add_executor_job(api.info)
                _LOGGER.debug(f'{DOMAIN}: sensor: {response}')
            return {
                "last_regeneration": response.content["last_regeneration"],
                "nr_regenerations": response.content["nr_regenerations"],
                "last_maintenance": response.content["last_maintenance"],
                "total_volume": response.content["total_volume"],
            }
        except:
            raise SensorUpdateFailed

        
    hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name=DOMAIN,
        update_method=async_fetch_info,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=120),
    )

    # Fetch initial data so we have data when entities subscribe
    await hass.data[DOMAIN].async_refresh()
    return hass.data[DOMAIN]  

class SensorUpdateFailed(exceptions.HomeAssistantError):
    """Error to indicate we get invalid data from the nas."""    