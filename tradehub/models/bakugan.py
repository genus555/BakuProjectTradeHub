from django.db import models
from .attribute import Attribute
from .user import User

class Bakugan(models.Model):
    name = models.CharField(max_length=60)
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
            return Bakugan.get_all_bakugan()

    class Meta:
        verbose_name = "Bakugan"
        verbose_name_plural = "Bakugans"
    
    def __str__(self):
        return f"{self.attribute} {self.name}"

class OwnedBakugan(models.Model):
    bakugan = models.ForeignKey(Bakugan, on_delete=models.CASCADE)
    power = models.IntegerField(default=320)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory")
    trade_type = models.CharField(max_length=10, choices=[("trading", "Trading"), ("selling", "Selling"), ("both", "Both")])
    is_offered = models.BooleanField(default=False)

    @staticmethod
    def get_owned_bakugan_by_id(ids):
        return OwnedBakugan.objects.filter(id__in=ids)
    
    @staticmethod
    def get_all_owned_bakugan():
        return OwnedBakugan.objects.all().order_by('owner')

    class Meta:
        verbose_name = "OwnedBakugan"
        verbose_name_plural = "OwnedBakugans"
    
    def __str__(self):
        return f"{self.owner}'s {self.power} {self.bakugan.attribute} {self.bakugan.name}"