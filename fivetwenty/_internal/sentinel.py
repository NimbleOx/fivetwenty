"""Distinguish an omitted request field from an explicit JSON null."""

from enum import Enum


class UnsetType(Enum):
    """Type of the omitted-value sentinel used in endpoint defaults."""

    UNSET = "UNSET"

    def __repr__(self) -> str:
        return "UNSET"


UNSET = UnsetType.UNSET
