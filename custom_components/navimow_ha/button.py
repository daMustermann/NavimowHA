"""Button platform for Navimow integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from mower_sdk.api import MowerAPI
from mower_sdk.models import MowerCommand

from .const import DOMAIN
from .coordinator import NavimowCoordinator

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="locate",
        translation_key="locate",
        entity_category="action",
    ),
    ButtonEntityDescription(
        key="restart",
        translation_key="restart",
        entity_category="action",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow button entities from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api: MowerAPI = data["api"]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        for description in BUTTON_DESCRIPTIONS:
            entities.append(
                NavimowButton(
                    coordinator=coordinators[device.id],
                    api=api,
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowButton(CoordinatorEntity[NavimowCoordinator], ButtonEntity):
    """Representation of a Navimow action button."""

    entity_description: ButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        api: MowerAPI,
        entity_description: ButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self.entity_description = entity_description

        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_{entity_description.key}_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=device.name,
            manufacturer="Navimow",
            model=device.model or "Unknown",
            sw_version=device.firmware_version or None,
            serial_number=device.serial_number or device.id,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.get_device_state() is not None

    async def async_press(self) -> None:
        """Handle button press."""
        key = self.entity_description.key
        command_map = {
            "locate": MowerCommand.LOCATE,
            "restart": MowerCommand.RESTART,
        }
        command = command_map.get(key)
        if command is not None:
            await self._send_command(command)

    async def _send_command(self, command: MowerCommand) -> None:
        await self.coordinator._async_ensure_valid_token()
        try:
            await self._api.async_send_command(self.coordinator.device.id, command)
            _LOGGER.info("Button pressed: %s", self.entity_description.key)
        except Exception as err:
            _LOGGER.error(
                "Failed to send command %s: %s", self.entity_description.key, err
            )
            raise
