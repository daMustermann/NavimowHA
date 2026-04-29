"""Button platform for Navimow integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

import uuid

from mower_sdk.models import DeviceCommandMessage

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
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        for description in BUTTON_DESCRIPTIONS:
            entities.append(
                NavimowButton(
                    coordinator=coordinators[device.id],
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
        entity_description: ButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)
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
        sdk = self.coordinator.sdk
        device_id = self.coordinator.device.id
        key = self.entity_description.key
        command = DeviceCommandMessage(
            id=f"cmd-{uuid.uuid4()}",
            device_id=device_id,
            command=key,
            params={},
        )
        try:
            await self.hass.async_add_executor_job(sdk._publish_command, command)
            _LOGGER.info("Button pressed: %s for device %s", key, device_id)
        except Exception as err:
            _LOGGER.error(
                "Failed to send command %s: %s", key, err
            )
            raise
