"""Sensor platform for Navimow integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NavimowCoordinator


@dataclass(frozen=True, kw_only=True)
class NavimowSensorEntityDescription(SensorEntityDescription):
    """Describes Navimow sensor entity."""

    value_fn: Callable[[NavimowCoordinator], Any]


SENSOR_DESCRIPTIONS: tuple[NavimowSensorEntityDescription, ...] = (
    NavimowSensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda coordinator: (
            state.battery if (state := coordinator.get_device_state()) else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="signal_strength",
        translation_key="signal_strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda coordinator: (
            state.signal_strength if (state := coordinator.get_device_state()) else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="status",
        translation_key="status",
        value_fn=lambda coordinator: (
            state.state if (state := coordinator.get_device_state()) else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="position_x",
        translation_key="position_x",
        native_unit_of_measurement="m",
        value_fn=lambda coordinator: (
            state.position.get("postureX") if (state := coordinator.get_device_state()) and state.position else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="position_y",
        translation_key="position_y",
        native_unit_of_measurement="m",
        value_fn=lambda coordinator: (
            state.position.get("postureY") if (state := coordinator.get_device_state()) and state.position else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="position_theta",
        translation_key="position_theta",
        native_unit_of_measurement="rad",
        value_fn=lambda coordinator: (
            state.position.get("postureTheta") if (state := coordinator.get_device_state()) and state.position else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="error_code",
        translation_key="error_code",
        value_fn=lambda coordinator: (
            state.error.get("code") if (state := coordinator.get_device_state()) and state.error else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="error_message",
        translation_key="error_message",
        value_fn=lambda coordinator: (
            state.error.get("message") if (state := coordinator.get_device_state()) and state.error else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="work_time",
        translation_key="work_time",
        native_unit_of_measurement="s",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda coordinator: (
            state.metrics.get("workTime") if (state := coordinator.get_device_state()) and state.metrics else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="work_area",
        translation_key="work_area",
        native_unit_of_measurement="m²",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda coordinator: (
            state.metrics.get("workArea") if (state := coordinator.get_device_state()) and state.metrics else None
        ),
    ),
    NavimowSensorEntityDescription(
        key="timestamp",
        translation_key="timestamp",
        value_fn=lambda coordinator: (
            state.timestamp if (state := coordinator.get_device_state()) else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow sensors from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities: list[NavimowSensor] = []
    for device in devices:
        coordinator = coordinators[device.id]
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                NavimowSensor(
                    coordinator=coordinator,
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowSensor(CoordinatorEntity[NavimowCoordinator], SensorEntity):
    """Representation of a Navimow sensor."""

    entity_description: NavimowSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        entity_description: NavimowSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_{entity_description.key}"
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
    def native_value(self) -> Any:
        """Return sensor value from coordinator."""
        return self.entity_description.value_fn(self.coordinator)
