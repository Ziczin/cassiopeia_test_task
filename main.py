from datetime import datetime
from dataset import CATEGORIES, PRODUCTS
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD

import os
import django
from django.conf import settings

settings.configure(
    SECRET_KEY='any-key',
    INSTALLED_APPS=['rest_framework'],
)
django.setup()

from rest_framework.serializers import (
    Serializer,
    IntegerField as Integer,
    CharField as Char,
    SlugField as Slug,
    DecimalField as Decimal,
    BooleanField as Boolean,
    URLField as URL,
    ValidationError,
)


class FeedValidationError(ValidationError):
    """Ошибка валидации данных для YML-фида."""


class CategoryValidationError(FeedValidationError):
    """Ошибка в данных категории."""


class ProductValidationError(FeedValidationError):
    """Ошибка в данных товара."""


class CategoryRelationError(FeedValidationError):
    """Товар ссылается на несуществующую категорию."""


class CategorySerializer(Serializer):
    id = Integer(min_value=1)
    name = Char(min_length=1)
    is_active = Boolean()


class ProductSerializer(Serializer):
    id = Integer(min_value=1)
    name = Char(min_length=1)
    slug = Slug()
    category_id = Integer(min_value=1)
    price = Decimal(max_digits=10, decimal_places=2, min_value=0)
    old_price = Decimal(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        allow_null=True,
        required=False,
    )
    stock = Integer(min_value=0)
    description = Char(default="", allow_blank=True, required=False)
    image_url = URL(allow_null=True, required=False)
    is_active = Boolean()

def _validate_categories(categories):
    try:
        serializer = CategorySerializer(data=categories, many=True)
        serializer.is_valid(raise_exception=True)
    except ValidationError as error:
        raise CategoryValidationError(detail=error.detail) from error
    return serializer.validated_data


def _validate_products(products):
    try:
        serializer = ProductSerializer(data=products, many=True)
        serializer.is_valid(raise_exception=True)
    except ValidationError as error:
        raise ProductValidationError(detail=error.detail) from error
    return serializer.validated_data

def _validate_relations(products, categories):
    existing_ids = {category["id"] for category in categories}
    for product in products:
        if product["category_id"] not in existing_ids:
            raise CategoryRelationError(
                f'Товар id={product["id"]}: категория {product["category_id"]} не существует'
            )

def build_yml(products, categories, generated_at):

    if not isinstance(products, list) and (not product or all(isinstance(item, dict) for item in products)):
        raise TypeError("Expected")

    xml = '<?xml version="1.0" encoding="UTF-8"?>'


    return xml

def build_yml_old(products, categories, generated_at):
    xml = '<?xml version="1.0" encoding="UTF-8"?>'


    xml += f'<yml_catalog date="{generated_at}">'
    xml += "<shop>"

    xml += "<name>Test Shop</name>"
    xml += "<company>Test Company</company>"
    xml += "<url>https://example.test</url>"

    xml += '<currencies><currency id="RUB" rate="1"/></currencies>'

    xml += "<categories>"

    for product in products:
        category = next(
            category
            for category in categories
            if category["id"] == product["category_id"]
        )

        xml += (
            f'<category id="{category["id"]}">'
            f'{category["name"]}'
            f"</category>"
        )

    xml += "</categories>"
    xml += "<offers>"

    for product in products:
        xml += (
            f'<offer id="{product["id"]}" '
            f'available="{product["stock"]}">'
        )

        xml += (
            f"<url>"
            f'https://example.test/products/{product["slug"]}/'
            f"</url>"
        )

        price = product["price"].replace(".", ",")

        xml += f"<price>{price}</price>"

        if product["old_price"]:
            xml += f'<oldprice>{product["old_price"]}</oldprice>'

        xml += "<currencyId>RUB</currencyId>"
        xml += f'<categoryId>{product["category_id"]}</categoryId>'
        xml += f'<picture>{product["image_url"]}</picture>'
        xml += f'<name>{product["name"]}</name>'
        xml += f'<description>{product["description"]}</description>'
        xml += "</offer>"

    xml += "</offers>"
    xml += "</shop>"
    xml += "</yml_catalog>"

    return xml


if __name__ == "__main__":
    result = build_yml(
        products=PRODUCTS,
        categories=CATEGORIES,
        generated_at=datetime(2026, 6, 18, 12, 0),
    )

    print(result)
    try:
        ET.fromstring(result.replace(""))
        print("Success etree")
    except Exception as e:
        print(f"Etree parse error:\n{e}")
