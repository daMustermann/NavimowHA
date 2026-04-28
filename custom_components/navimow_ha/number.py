"""Number platform for Navimow integration.

Exposes numeric mower settings as HA number entities so they can be
adjusted directly from the UI or via automations/scripts.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from mower_sdk.api import MowerAPI

from .const import DOMAIN
from .coordinator import NavimowCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class NavimowNumberEntityDescription(NumberEntityDescription):
    """Describes a Navimow number entity."""

    value_fn: Callable[[NavimowCoordinator], float | None] = lambda _: None
    set_attr_key: str = ""


NUMBER_DESCRIPTIONS: tuple[NavimowNumberEntityDescription, ...] = (
    NavimowNumberEntityDescription(
        key="cutting_height",
        translation_key="cutting_height",
        device_class=NumberDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        native_min_value=25,
        native_max_value=80,
        native_step=5,
        mode=NumberMode.SLIDER,
        set_attr_key="bladeHeight",
        value_fn=lambda coordinator: (
            attrs.attributes.get("bladeHeight")
            if (attrs := coordinator.get_device_attributes())
            and attrs.attributes
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow number entities from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api: MowerAPI = data["api"]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities: list[NavimowNumber] = []
    for device in devices:
        for description in NUMBER_DESCRIPTIONS:
            entities.append(
                NavimowNumber(
                    coordinator=coordinators[device.id],
                    api=api,
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowNumber(CoordinatorEntity[NavimowCoordinator], NumberEntity):
    """Numeric setting entity for a Navimow mower."""

    entity_description: NavimowNumberEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        api: MowerAPI,
        entity_description: NavimowNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self.entity_description = entity_description

        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_{entity_description.key}_number"
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
    def native_value(self) -> float | None:
        """Return the current value from coordinator data."""
        return self.entity_description.value_fn(self.coordinator)

    async def async_set_native_value(self, value: float) -> None:
        """Push the new value to the mower via REST API."""
        attr_key = self.entity_description.set_attr_key
        if not attr_key:
            _LOGGER.error("No attribute key defined for %s", self.entity_description.key)
            return
        await self.coordinator._async_ensure_valid_token()
        try:
            await self._api.async_set_device_attribute(
                self.coordinator.device.id, attr_key, int(value)
            )
            _LOGGER.info(
                "Set %s to %s for device %s",
                attr_key,
                value,
                self.coordinator.device.id,
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", attr_key, value, err)
            raise
