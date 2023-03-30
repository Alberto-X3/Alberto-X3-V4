__all__ = (
    "AllColors",
    "FlatUIColors",
    "MaterialColors",
)


from abc import ABC
from typing import Any, Callable, Generic, ItemsView, Iterator, TypeVar
from yaml import safe_load
from .constants import LIB_PATH
from .utils.essentials import get_logger


logger = get_logger()
T = TypeVar("T")


class NestedInt(int):
    """
    Integer with a read-only dictionary.
    """

    _values: dict[str | int, int]

    def __new__(cls, x: int, values: dict[str | int, int]):
        self = super().__new__(cls, x)
        self._values = values
        return self

    def __getitem__(self, item: str | int) -> int:
        return self._values[item]

    def __iter__(self) -> Iterator[str | int]:
        return self._values.__iter__()

    def items(self) -> ItemsView:
        return self._values.items()

    def __copy__(self) -> int:
        return int(self)

    def __deepcopy__(self, *_: Any) -> int:
        return int(self)


_color_data_flat_ui: dict[str, int]
_color_data_flat_ui = safe_load(LIB_PATH.joinpath("colors/flat_ui.yml").read_text("utf-8"))
_color_data_material: dict[str, dict[str | int, int]]
_color_data_material = safe_load(LIB_PATH.joinpath("colors/material.yml").read_text("utf-8"))


def _load_flat_ui(name: str) -> int:
    return _color_data_flat_ui[name]


def _load_material(name: str) -> NestedInt:
    data = _color_data_material[name]
    return NestedInt(data[500], data)


class BaseColor(ABC, Generic[T]):
    """
    Automatically loads every color in a directly subclassed class.
    """

    _load: Callable[[str], T]

    def __init_subclass__(cls) -> None:
        if cls.__base__ != BaseColor:
            # already subclassed
            return

        for color in cls.__annotations__:
            if color.startswith("_"):
                continue
            setattr(cls, color, cls._load(color))
        logger.info(f"Loaded colors for {cls.__name__}")


class FlatUIColors(BaseColor[int]):
    """
    All Flat-UI-Colors (https://materialui.co/flatuicolors).
    """

    __slots__ = ()
    _load = _load_flat_ui

    turquoise: int
    greensea: int
    emerland: int
    nephritis: int
    peterriver: int
    belizehole: int
    amethyst: int
    wisteria: int
    wetasphalt: int
    midnightblue: int
    sunflower: int
    orange: int
    carrot: int
    pumpkin: int
    alizarin: int
    pomegranate: int
    clouds: int
    silver: int
    concrete: int
    asbestos: int


class MaterialColors(BaseColor[NestedInt]):
    """
    All Material-Colors (https://materialui.co/colors).
    """

    __slots__ = ()
    _load = _load_material

    red: NestedInt
    pink: NestedInt
    purple: NestedInt
    deeppurple: NestedInt
    indigo: NestedInt
    blue: NestedInt
    lightblue: NestedInt
    cyan: NestedInt
    teal: NestedInt
    green: NestedInt
    lightgreen: NestedInt
    lime: NestedInt
    yellow: NestedInt
    amber: NestedInt
    orange: NestedInt
    deeporange: NestedInt
    brown: NestedInt
    grey: NestedInt
    bluegrey: NestedInt


class AllColors(FlatUIColors, MaterialColors):
    """
    Flat-UI-Colors and Material-Colors combined.

    Notes
    -----
    There is a name-conflict with ``orange``. The value from ``MaterialColors`` will be set since it's more detailed.
    """

    # in case I want to change something about the empty __slots__
    __slots__ = FlatUIColors.__slots__ + MaterialColors.__slots__  # value: ()

    orange: NestedInt = MaterialColors.orange

    default: int = MaterialColors.teal[600]
    error: int = MaterialColors.red["a700"]
    warning: int = MaterialColors.yellow["a200"]
    assertion: int = MaterialColors.orange[900]
    notimplemented: int = MaterialColors.lightblue[900]
    missing_permissions: int = MaterialColors.indigo["a700"]

    blurple: int = 0x5865F2
    blurple_legacy: int = 0x7289DA

    albertunruh: int = 0x3C62F9
