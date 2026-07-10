from django.db import models
from .attribute import Attribute

class Bakugan(models.Model):
    name = models.CharField(max_length=60)
    price = models.IntegerField(default=4000)
    power = models.IntegerField(default=320)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='uploads/bakugans/')

    @staticmethod
    def get_bakugan_by_id(ids):
        return Bakugan.objects.filter(id__in=ids)
    
    @staticmethod
    def get_all_bakugan():
        return Bakugan.objects.all().order_by('name')
    
    @staticmethod
    def get_all_bakugan_by_attributeid(attribute_id):
        if attribute_id:
            return Bakugan.objects.filter(attribute=attribute_id).order_by('name')
        else:
            return Bakugan.get_all_products()
        
    @staticmethod
    def get_bakugan_price_total(bakugans):
        total = 0
        for bakugan in bakugans:
            total += bakugan.price
        return total

    class Meta:
        verbose_name = "Bakugan"
        verbose_name_plural = "Bakugans"
    
    def __str__(self):
        return f"{self.attribute} {self.name}"