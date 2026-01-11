"""Data validation for the tenant management system.

Provides validation logic for buildings, apartments, and tenant data.
All validation rules are configuration-driven with no hardcoded values.
"""

from typing import Dict, Any, List, Tuple
from datetime import date

from src.config import get_config
from src.exceptions import ValidationError


class DataValidator:
    """Validator for tenant management data."""

    def __init__(self):
        """Initialize validator with configuration."""
        self._config = get_config()
        self._buildings_config = self._config.get("buildings", [])

    def get_valid_building_numbers(self) -> List[int]:
        """Get list of valid building numbers from configuration."""
        return sorted([bldg.get("number", 0) for bldg in self._buildings_config])

    def get_apartment_count(self, building_number: int) -> int:
        """Get apartment count for a building."""
        for bldg in self._buildings_config:
            if bldg.get("number") == building_number:
                return bldg.get("total_apartments", 0)
        return 0

    def validate_building_number(self, building_number: int) -> bool:
        """Validate that building number exists in configuration."""
        valid_buildings = self.get_valid_building_numbers()
        if building_number not in valid_buildings:
            raise ValidationError(
                f"Invalid building number: {building_number}",
                {"valid_buildings": valid_buildings}
            )
        return True

    def validate_apartment_number(
        self, building_number: int, apartment_number: int
    ) -> bool:
        """Validate apartment number is within range for building."""
        self.validate_building_number(building_number)
        max_apartments = self.get_apartment_count(building_number)
        if apartment_number < 1 or apartment_number > max_apartments:
            raise ValidationError(
                f"Invalid apartment number: {apartment_number}",
                {"building": building_number, "max_apartments": max_apartments}
            )
        return True

    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format."""
        cleaned = phone.replace("-", "").replace(" ", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValidationError(
                "Phone number must contain only digits",
                {"phone": phone}
            )
        min_len = self._config.get("validation.phone_min_length", 9)
        max_len = self._config.get("validation.phone_max_length", 15)
        if len(cleaned) < min_len or len(cleaned) > max_len:
            raise ValidationError(
                f"Phone must be {min_len}-{max_len} digits",
                {"phone": phone, "length": len(cleaned)}
            )
        return True

    def validate_dates(
        self, move_in: date, move_out: date = None
    ) -> bool:
        """Validate move-in and move-out dates."""
        if move_out and move_out < move_in:
            raise ValidationError(
                "Move-out date cannot be before move-in date",
                {"move_in": str(move_in), "move_out": str(move_out)}
            )
        return True

    def validate_parking_slots(self, slot1: str, slot2: str) -> bool:
        """Validate parking slot format."""
        for slot in [slot1, slot2]:
            if slot and not slot.strip():
                raise ValidationError(
                    "Parking slot cannot be empty string",
                    {"slot": slot}
                )
        return True

    def validate_tenant_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete tenant data dictionary."""
        errors = []
        try:
            self.validate_building_number(data.get("building_number", 0))
        except ValidationError as e:
            errors.append(str(e))
        try:
            self.validate_apartment_number(
                data.get("building_number", 0),
                data.get("apartment_number", 0)
            )
        except ValidationError as e:
            errors.append(str(e))
        try:
            if data.get("phone"):
                self.validate_phone_number(data["phone"])
        except ValidationError as e:
            errors.append(str(e))
        if not data.get("first_name", "").strip():
            errors.append("First name is required")
        if not data.get("last_name", "").strip():
            errors.append("Last name is required")
        if not data.get("is_owner", True):
            owner_info = data.get("owner_info", {})
            if not owner_info:
                errors.append("Owner info required for renters")
            elif not owner_info.get("first_name"):
                errors.append("Owner first name required")
            elif not owner_info.get("last_name"):
                errors.append("Owner last name required")
        return len(errors) == 0, errors

    def validate_ownership_change(
        self, change_date: date, current_move_in: date
    ) -> bool:
        """Validate ownership change date."""
        if change_date < current_move_in:
            raise ValidationError(
                "Ownership change date cannot be before current move-in",
                {"change_date": str(change_date), "move_in": str(current_move_in)}
            )
        return True
