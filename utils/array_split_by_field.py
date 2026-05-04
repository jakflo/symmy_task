from typing import Any, List, Iterable, TypedDict


class SplitResult(TypedDict):
    have: List[Any]
    havent: List[Any]

def split_by_fields(
    items: List[Any],
    field_name: str,
    field_values: Iterable[Any],
) -> SplitResult:
    values_set = set(field_values)  # rychlé lookupy

    result: SplitResult = {
        "have": [],
        "havent": [],
    }

    for item in items:
        has_value = False

        if isinstance(item, dict):
            has_value = item.get(field_name) in values_set
        else:
            if hasattr(item, field_name):
                has_value = getattr(item, field_name) in values_set

        if has_value:
            result["have"].append(item)
        else:
            result["havent"].append(item)

    return result

def split_by_field(
    items: List[Any],
    field_name: str,
    field_value
) -> SplitResult:
    return split_by_fields(items, field_name, [field_value])
