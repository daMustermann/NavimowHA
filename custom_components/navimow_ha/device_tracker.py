"""Device tracker platform for Navimow integration."""
from __future__ import annotations

from homeassistant.components.device_tracker import (
    SourceType,
    TrackerEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
            )
        )
    async_add_entities(entities)


class NavimowDeviceTracker(
    CoordinatorEntity[NavimowCoordinator], TrackerEntity
):
    """GPS tracker entity for a Navimow mower.

    Note: the coordinates reported here are *local* to the mowing area
    (meters from the charging station), not real GPS coordinates.  The
    device tracker is still useful to visualise the mower's position on
    the HA map card relative to where it started.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: NavimowCoordinator) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{DOMAIN}_{device.id}_location"
        self._attr_name = "Position"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=device.name,
            manufacturer="Navimow",
            model=device.model or "Unknown",
            sw_version=device.firmware_version or None,
            serial_number=device.serial_number or device.id,
        )

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def available(self) -> bool:
        """Entity stays available as long as we have cached position data."""
        state = self.coordinator.get_device_state()
        if state is not None and state.position:
            return True
        return super().available

    @property
    def latitude(self) -> float | None:
        """Return the Y coordinate (maps to latitude in HA map)."""
        state = self.coordinator.get_device_state()
        if not state or not state.position:
            return None
        return state.position.get("postureY")

    @property
    def longitude(self) -> float | None:
        """Return the X coordinate (maps to longitude in HA map)."""
        state = self.coordinator.get_device_state()
        if not state or not state.position:
            return None
        return state.position.get("postureX")

    @property
    def gps_accuracy(self) -> float:
        """Return a fixed accuracy value (coordinates are local, not GPS)."""
        return 0.5

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra location attributes."""
        state = self.coordinator.get_device_state()
        if not state or not state.position:
            return {}
        attrs: dict = {
            "posture_x": state.position.get("postureX"),
            "posture_y": state.position.get("postureY"),
            "posture_theta": state.position.get("postureTheta"),
        }
        if state.position.get("mapId"):
            attrs["map_id"] = state.position.get("mapId")
        return attrs

    @property
    def force_update(self) -> bool:
        """Force state update on every coordinator refresh."""
        return True
