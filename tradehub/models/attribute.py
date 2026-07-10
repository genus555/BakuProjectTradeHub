from django.db import models

class Attribute(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='uploads/attributes/', blank=True, null=True)

    @staticmethod
    def get_all_attributes():
        return Attribute.objects.all()
    
    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
    
    def __str__(self):
        return self.name