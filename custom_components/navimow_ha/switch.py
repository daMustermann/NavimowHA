"""Switch platform for Navimow integration."""
from __future__ import annotations

import logging
import uuid

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from mower_sdk.models import DeviceCommandMessage

from .const import DOMAIN
from .coordinator import NavimowCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="edge_mowing",
        translation_key="edge_mowing",
    ),
    SwitchEntityDescription(
        key="rain_mode",
        translation_key="rain_mode",
    ),
    SwitchEntityDescription(
        key="anti_theft",
        translation_key="anti_theft",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow switch entities from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        for description in SWITCH_DESCRIPTIONS:
            entities.append(
                NavimowSwitch(
                    coordinator=coordinators[device.id],
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowSwitch(CoordinatorEntity[NavimowCoordinator], SwitchEntity):
    """Representation of a Navimow switch."""

    entity_description: SwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_{entity_description.key}_switch"
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

    @property
    def is_on(self) -> bool | None:
        attrs = self.coordinator.get_device_attributes()
        if not attrs or not attrs.attributes:
            return None
        value = attrs.attributes.get(self.entity_description.key)
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._send_command(self.entity_description.key, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._send_command(self.entity_description.key, False)

    async def _send_command(self, attribute: str, value: bool) -> None:
        """Send a command via MQTT to toggle a device attribute."""
        sdk = self.coordinator.sdk
        device_id = self.coordinator.device.id
        command = DeviceCommandMessage(
            id=f"cmd-{uuid.uuid4()}",
            device_id=device_id,
            command=f"set_{attribute}",
            params={"enabled": value},
        )
        try:
            await self.hass.async_add_executor_job(sdk._publish_command, command)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s=%s: %s", attribute, value, err)
            raise
