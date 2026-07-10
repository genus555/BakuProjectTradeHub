from django.core.management.base import BaseCommand
from tradehub.models.attribute import Attribute
from tradehub.models.bakugan import Bakugan
import json

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        
        with open("old_categories.json") as f:
            old_categories = json.load(f)

        category_id_map = {}
        for entry in old_categories:
            old_id = entry["pk"]
            name = entry["fields"]["name"]
            old_image_path = entry["fields"]["image"]
            new_image_path = old_image_path.replace("uploads/categories", "uploads/attributes")
            attribute = Attribute.objects.create(name=name, image=new_image_path)
            category_id_map[old_id] = attribute

        with open("old_products.json") as f:
            old_products = json.load(f)

        for entry in old_products:
            fields = entry["fields"]
            old_category_id = fields["category"]
            old_image_path = fields["image"]
            new_image_path = old_image_path.replace("uploads/products", "uploads/bakugans")
            Bakugan.objects.create(
                name=fields["name"],
                attribute=category_id_map[old_category_id],
                image=new_image_path,
            )