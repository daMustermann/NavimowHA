"""Binary sensor platform for Navimow integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NavimowCoordinator


@dataclass(frozen=True, kw_only=True)
class NavimowBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Navimow binary sensor entity."""

    value_fn: Callable[[NavimowCoordinator], bool | None] = lambda _: None


BINARY_SENSOR_DESCRIPTIONS: tuple[NavimowBinarySensorEntityDescription, ...] = (
    NavimowBinarySensorEntityDescription(
        key="error",
        translation_key="error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda coordinator: (
            (state := coordinator.get_device_state()) is not None
            and state.error is not None
        ),
    ),
    NavimowBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda coordinator: (
            (state := coordinator.get_device_state()) is not None
            and state.state in ("charging", "docked")
        ),
    ),
    NavimowBinarySensorEntityDescription(
        key="mowing",
        translation_key="mowing",
        value_fn=lambda coordinator: (
            (state := coordinator.get_device_state()) is not None
            and state.state == "mowing"
        ),
    ),
    NavimowBinarySensorEntityDescription(
        key="docked",
        translation_key="docked",
        value_fn=lambda coordinator: (
            (state := coordinator.get_device_state()) is not None
            and state.state in ("docked", "charging")
        ),
    ),
    NavimowBinarySensorEntityDescription(
        key="returning",
        translation_key="returning",
        value_fn=lambda coordinator: (
            (state := coordinator.get_device_state()) is not None
            and state.state == "returning"
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow binary sensors from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities: list[NavimowBinarySensor] = []
    for device in devices:
        coordinator = coordinators[device.id]
        for description in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(
                NavimowBinarySensor(
                    coordinator=coordinator,
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowBinarySensor(CoordinatorEntity[NavimowCoordinator], BinarySensorEntity):
    """Representation of a Navimow binary sensor."""

    entity_description: NavimowBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        entity_description: NavimowBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_{entity_description.key}_binary"
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
        if self.coordinator.get_device_state() is not None:
            return True
        return super().available

    @property
    def is_on(self) -> bool | None:
        """Return True when the condition described by this sensor is active."""
        return self.entity_description.value_fn(self.coordinator)
