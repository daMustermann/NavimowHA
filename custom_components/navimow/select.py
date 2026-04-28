"""Select platform for Navimow integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from mower_sdk.api import MowerAPI

from .const import DOMAIN
from .coordinator import NavimowCoordinator

_LOGGER = logging.getLogger(__name__)

CUTTING_HEIGHT_OPTIONS = [
    "25 mm",
    "30 mm",
    "35 mm",
    "40 mm",
    "45 mm",
    "50 mm",
    "55 mm",
    "60 mm",
    "65 mm",
    "70 mm",
    "75 mm",
    "80 mm",
]

SELECT_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="cutting_height",
        translation_key="cutting_height",
        options=CUTTING_HEIGHT_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow select entities from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api: MowerAPI = data["api"]
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        for description in SELECT_DESCRIPTIONS:
            entities.append(
                NavimowSelect(
                    coordinator=coordinators[device.id],
                    api=api,
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowSelect(CoordinatorEntity[NavimowCoordinator], SelectEntity):
    """Representation of a Navimow select entity."""

    entity_description: SelectEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        api: MowerAPI,
        entity_description: SelectEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._api = api
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
        return self.coordinator.get_device_state() is not None

    @property
    def options(self) -> list[str]:
        return CUTTING_HEIGHT_OPTIONS

    @property
    def current_option(self) -> str | None:
        attrs = self.coordinator.get_device_attributes()
        if not attrs or not attrs.attributes:
            return None
        cutting_height = attrs.attributes.get("bladeHeight")
        if cutting_height is not None:
            return f"{cutting_height} mm"
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected cutting height."""
        # Parse the numeric value from the option string (e.g. "35 mm" -> 35)
        try:
            height_mm = int(option.split()[0])
        except (ValueError, IndexError):
            _LOGGER.error("Invalid cutting height option: %s", option)
            return
        await self.coordinator._async_ensure_valid_token()
        try:
            await self._api.async_set_device_attribute(
                self.coordinator.device.id, "bladeHeight", height_mm
            )
            _LOGGER.info(
                "Cutting height set to %d mm for device %s",
                height_mm,
                self.coordinator.device.id,
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to set cutting height to %d mm: %s", height_mm, err
            )
            raise
