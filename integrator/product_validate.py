from rest_framework import serializers
from typing import Dict
from .product_type import StockValue, Color, ProductTransformed
import json
from hashlib import md5

vat_rate = 0.21

class AttributesSerializer(serializers.Serializer):
    color = serializers.CharField(required=False, allow_null=True, allow_blank=True)

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    price_vat_excl = serializers.FloatField()
    stocks = serializers.DictField()
    attributes = AttributesSerializer(required=False, allow_null=True)

    # --- FIELD VALIDATION ---

    def validate_title(self, value: str):
        if len(value) < 3 or len(value) > 100:
            raise serializers.ValidationError("title length must be 3-100")
        return value

    def validate_price_vat_excl(self, value: float):
        if value < 0:
            raise serializers.ValidationError("price_vat_excl cannot be negative")
        return value

    def validate_stocks(self, value: Dict[str, StockValue]):
        for key, v in value.items():
            if not (isinstance(v, int) or v == "N/A"):
                raise serializers.ValidationError(
                    f"stocks['{key}'] musí být int nebo 'N/A'"
                )
        return value

    # --- OBJECT VALIDATION ---

    def validate(self, attrs):
        return attrs

    # --- COMPUTED FIELDS ---

    def get_sum_stocks(self, obj) -> int:
        total = 0
        for value in obj.get("stocks", {}).values():
            if isinstance(value, int):
                total += value
        return total

    def get_color(self, obj) -> Color:
        attributes = obj.get("attributes")
        if attributes and attributes.get("color"):
            return attributes["color"]
        return "N/A"

    def get_price(self, obj) -> float:
        return round(obj["price_vat_excl"] * (1 + vat_rate), 2)

    # --- TRANSFORMACE ---

    def to_representation(self, instance) -> ProductTransformed:
        data = super().to_representation(instance)

        result = {
            "source_id": data["id"],
            "title": data["title"],
            "price": self.get_price(data),
            "stocks": self.get_sum_stocks(data),
            "color": self.get_color(data),
        }

        result["hash"] = md5(
            json.dumps(result, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return result