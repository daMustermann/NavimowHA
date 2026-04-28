"""Select platform for Navimow integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NavimowCoordinator

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
    devices = data["devices"]
    coordinators: dict[str, NavimowCoordinator] = data["coordinators"]

    entities = []
    for device in devices:
        for description in SELECT_DESCRIPTIONS:
            entities.append(
                NavimowSelect(
                    coordinator=coordinators[device.id],
                    entity_description=description,
                )
            )
    async_add_entities(entities)


class NavimowSelect(SelectEntity):
    """Representation of a Navimow select."""

    entity_description: SelectEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        super().__init__()
        self.coordinator = coordinator
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