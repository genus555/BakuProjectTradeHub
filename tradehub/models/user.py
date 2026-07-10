from django.db import models

class User(models.Model):
    ign = models.CharField(max_length=50)
    discord_name = models.CharField(max_length=50)
    otp_secret = models.CharField(max_length=32)

    def register(self):
        self.save()
    
    @staticmethod
    def get_user_by_in_game_name(ign):
        try:
            return User.objects.get(ign=ign)
        except User.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_by_discord_name(discord_name):
        try:
            return User.objects.get(discord_name=discord_name)
        except User.DoesNotExist:
            return False
    
    def isExists(self):
        return User.objects.filter(ign=self.ign).exists()
    
    def get_user_inventory():
        return User.inventory.all()
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.ign} | {self.discord_name}"