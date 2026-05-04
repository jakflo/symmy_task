from django.db import models
from typing import List

class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_id = models.CharField(max_length=14, unique=True)
    title = models.CharField(max_length=100)
    price = models.FloatField()
    stocks = models.IntegerField()
    color = models.CharField(max_length=40)
    hash = models.CharField(max_length=32)

    @classmethod
    def get_data_fields(cls):
        return [
            field.name
            for field in cls._meta.fields
            if field.name not in ("id", "source_id", "hash")
        ]

    class Meta:
        db_table = "items"
        indexes = [
            models.Index(fields=["source_id"], name="items_source_id"),
        ]        
