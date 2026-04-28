"""Device tracker platform for Navimow integration."""
from __future__ import annotations

from homeassistant.components.device_tracker import (
    TrackerSourceType,
)
from homeassistant.components.device_tracker.config_entry import (
    BaseDeviceTracker,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NavimowCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow device tracker from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        entities.append(
            NavimowDeviceTracker(
                coordinator=coordinators[device.id],
                device_id=device.id,
                device_name=device.name,
                device_info=device,
            )
        )
    async_add_entities(entities)


class NavimowDeviceTracker(BaseDeviceTracker):
    """Representation of a Navimow device tracker."""

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        device_id: str,
        device_name: str,
        device_info,
    ) -> None:
        """Initialize the device tracker."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._device_name = device_name
        self._device_info = device_info
        self._attr_unique_id = f"{DOMAIN}_{device_id}_location"
        self._attr_name = f"{device_name} Position"

    @property
    def source_type(self) -> TrackerSourceType:
        """Return the source type."""
        return TrackerSourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude (local map coordinate)."""
        state = self.coordinator.get_device_state()
        if not state or not state.position:
            return None
        return state.position.get("postureY")

    @property
    def longitude(self) -> float | None:
        """Return longitude (local map coordinate)."""
        state = self.coordinator.get_device_state()
        if not state or not state.position:
            return None
        return state.position.get("postureX")

    @property
    def gps_accuracy(self) -> float:
        """Return GPS accuracy (local coordinates, not real GPS)."""
        return 0.5

    @property
    def location_attributes(self) -> dict:
        """Return extra location attributes."""
        state = self.coordinator.get_device_state()
        attrs = {}
        if state and state.position:
            attrs = {
                "posture_x": state.position.get("postureX"),
                "posture_y": state.position.get("postureY"),
                "posture_theta": state.position.get("postureTheta"),
            }
            if state.position.get("mapId"):
                attrs["map_id"] = state.position.get("mapId")
        return attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Navimow",
            model=self._device_info.model or "Unknown",
            sw_version=self._device_info.firmware_version or None,
            serial_number=self._device_info.serial_number or self._device_id,
        )

    @property
    def force_update(self) -> bool:
        """Return if updates should be forced."""
        return True