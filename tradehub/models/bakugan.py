from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .attribute import Attribute
from .user import User

class Bakugan(models.Model):
    name = models.CharField(max_length=60)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, default=1)  
    image = models.ImageField(upload_to='uploads/bakugans/')

    @staticmethod
    def get_bakugan_by_id(id):
        return Bakugan.objects.get(id=id)
    
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
    price = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory")
    trade_type = models.CharField(max_length=10, choices=[("trading", "Trading"), ("selling", "Selling"), ("both", "Both")])
    is_offered = models.BooleanField(default=False)

    def create(self):
        self.save()

    def edit(self, data):
        try:
            for field, value in data.items():
                if hasattr(self, field):
                    setattr(self, field, value)
            self.save()
            return True
        except Exception:
            return False

    @staticmethod
    def get_owned_bakugans_by_attribute(attribute):
        return OwnedBakugan.objects.filter(bakugan__attribute=attribute)
    
    @staticmethod
    def get_owned_bakugans_by_power(power):
        return OwnedBakugan.objects.filter(power__gte=power)
    
    @staticmethod
    def get_owned_bakugans_by_search(query):
        return OwnedBakugan.objects.filter(bakugan__name=query)
    @staticmethod
    def get_owned_bakugan_by_id(id):
        return OwnedBakugan.objects.get(id=id)
    
    @staticmethod
    def get_owned_bakugans_by_owner(owner_id):
        return OwnedBakugan.objects.filter(owner=owner_id)
    
    @staticmethod
    def get_all_owned_bakugan():
        return OwnedBakugan.objects.all().order_by('owner')

    class Meta:
        verbose_name = "OwnedBakugan"
        verbose_name_plural = "OwnedBakugans"
    
    def __str__(self):
        return f"{self.id} | {self.owner}'s {self.power} {self.bakugan.attribute} {self.bakugan.name}"