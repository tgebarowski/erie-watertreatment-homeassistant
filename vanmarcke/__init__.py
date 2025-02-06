"""Vanmarcke Treatment integration"""

import logging
from datetime import timedelta
import urllib3

import voluptuous as vol
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import HomeAssistantError

from erie_connect.client import ErieConnect

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

PLATFORMS = ["sensor", "binary_sensor"]

_LOGGER = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
})}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Erie IQ26 component."""
    _LOGGER.debug(f'{DOMAIN}: async_setup')
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Erie IQ26 from a config entry."""
    _LOGGER.debug(f'{DOMAIN}: async_setup_entry: entry {entry}')

    api = ErieConnect(
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        ErieConnect.Auth(
            entry.data[CONF_ACCESS_TOKEN],
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_UID],
            entry.data[CONF_EXPIRY]
        ),
        ErieConnect.Device(
            entry.data[CONF_DEVICE_ID],
            entry.data[CONF_DEVICE_NAME]
        ),
        verify_ssl=False  # Temporaire - À remplacer par True avec un certificat valide
    )

    coordinator = await create_coordinator(hass, api)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def create_coordinator(hass: HomeAssistant, api):
    """Create the data update coordinator."""
    async def async_fetch_info():
        try:
            async with async_timeout.timeout(120):
                response = await hass.async_add_executor_job(api.info)
                response_dashboard = await hass.async_add_executor_job(api.dashboard)
            return {
                "last_regeneration": response.content["last_regeneration"],
                "nr_regenerations": response.content["nr_regenerations"],
                "last_maintenance": response.content["last_maintenance"],
                "total_volume": response.content["total_volume"].split()[0],
                "warnings": response_dashboard.content["warnings"]
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    return DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_fetch_info,
        update_interval=timedelta(seconds=120),
    )

class SensorUpdateFailed(HomeAssistantError):
    """Error to indicate we get invalid data from the device."""
