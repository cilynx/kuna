"""Config flow to configure Kuna."""
from collections import OrderedDict
import logging

import voluptuous as vol

from .const import (
    CONF_RECORDING_INTERVAL,
    CONF_STREAM_INTERVAL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_RECORDING_INTERVAL,
    DEFAULT_STREAM_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class KunaFlowHandler(config_entries.ConfigFlow):
    """Handle a Kuna config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the Kuna config flow."""

    async def async_step_user(self, user_input=None):
        """Handle a user initiated flow."""
        errors = {}

        if self._async_current_entries():
            """Config entry currently exists, only one allowed."""
            return self.async_abort(reason="one_instance_only")

        if user_input is not None:
            """Validate the username and password by attempting to authenticate."""
            from . import KunaAccount

            kuna = KunaAccount(
                self.hass,
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
                async_get_clientsession(self.hass),
                user_input[CONF_RECORDING_INTERVAL],
            )
            if not await kuna.authenticate():
                """Authenticate has failed due to bad credentials or timeout."""
                errors["base"] = "auth_failed"
            else:
                """Authenticate is successful, create the config entry."""
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                        CONF_STREAM_INTERVAL: user_input[CONF_STREAM_INTERVAL],
                        CONF_RECORDING_INTERVAL: user_input[CONF_RECORDING_INTERVAL],
                    },
                )

        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_EMAIL)] = str
        data_schema[vol.Required(CONF_PASSWORD)] = str
        data_schema[
            vol.Optional(CONF_RECORDING_INTERVAL, default=DEFAULT_RECORDING_INTERVAL)
        ] = int
        data_schema[
            vol.Optional(CONF_STREAM_INTERVAL, default=DEFAULT_STREAM_INTERVAL)
        ] = int
        data_schema[
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL)
        ] = int

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )
