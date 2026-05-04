from typing import TypedDict, Dict, Union, Optional, Literal, NotRequired

StockValue = Union[int, Literal["N/A"]]
Color = Union[str, Literal["N/A"]]

class Attributes(TypedDict, total=False):
    color: str

class ProductType(TypedDict):
    id: str
    title: str
    price_vat_excl: float
    stocks: Dict[str, StockValue]
    attributes: Optional[Attributes]

class ProductTransformed(TypedDict):
    source_id: str
    title: str
    price: float
    stocks: int
    color: Color
    hash: str

class ProductTransformedWithoutHash(TypedDict):
    source_id: str
    title: str
    price: float
    stocks: int
    color: Color
    

class ProductTransformedForPatch(TypedDict):
    source_id: str
    title: NotRequired[str]
    price: NotRequired[float]
    stocks: NotRequired[int]
    color: NotRequired[Color]
    hash: NotRequired[str]