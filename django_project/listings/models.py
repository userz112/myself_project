from django.db import models



# Create your models here.

class HouseListing(models.Model):
    city = models.CharField(max_length=200,null=False)
    house_name = models.CharField(max_length=200,null=False)
    house_address = models.CharField(max_length=200,null=False)
    house_description = models.TextField(null=False)
    house_type = models.CharField(max_length=200,null=False)
    house_size = models.FloatField(null=False)
    house_height = models.CharField(max_length=200,null=False)
    house_position = models.CharField(max_length=200,null=False)
    total_price = models.FloatField(max_length=200,null=False)
    unit_price = models.FloatField(max_length=200,null=False)
    house_image = models.CharField(max_length=200,default="house_image/house_default.jpg")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "house_listing"
        verbose_name = "房源"
        verbose_name_plural = "房源"

    def __str__(self):
        return self.house_name


class FavoriteHouse(models.Model):
    user_id = models.IntegerField(null=False)
    house_listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorite_house"
        verbose_name = "收藏房源"
        verbose_name_plural = "收藏房源"

    def __str__(self):
        return f"用户 {self.user_id} 收藏了 {self.house_listing.house_name}"




