"""Button platform for Navimow integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from mower_sdk.api import MowerAPI
from mower_sdk.models import MowerCommand

from .const import DOMAIN
from .coordinator import NavimowCoordinator

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


class NavimowButton(ButtonEntity):
    """Representation of a Navimow button."""

    entity_description: ButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowCoordinator,
        api: MowerAPI,
        entity_description: ButtonEntityDescription,
    ) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.api = api
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
        key = self.entity_description.key
        if key == "locate":
            await self._send_command(MowerCommand.LOCATE)
        elif key == "restart":
            await self._send_command(MowerCommand.RESTART)

    async def _send_command(self, command: MowerCommand) -> None:
        import logging
        _LOGGER = logging.getLogger(__name__)
        await self.coordinator._async_ensure_valid_token()
        try:
            await self.api.async_send_command(self.coordinator.device.id, command)
            _LOGGER.info(f"Button pressed: {self.entity_description.key}")
        except Exception as err:
            _LOGGER.error(f"Failed to send command {self.entity_description.key}: {err}")