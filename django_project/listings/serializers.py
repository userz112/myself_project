from rest_framework import serializers
from .models import HouseListing, FavoriteHouse

class HouseListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseListing
        fields = '__all__'
        read_only_fields = ['created_time']
        extra_kwargs = {'house_image': {'read_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('house_image') and not data['house_image'].startswith('http'):
            data['house_image'] = '/media/' + data['house_image']
        return data

class FavoriteHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteHouse
        fields = '__all__'
        read_only_fields = ['created_time']

    def check_user_favorites(self, user_id):
        ids = FavoriteHouse.objects.filter(user_id=user_id).values_list('house_listing_id', flat=True)
        houses = HouseListing.objects.filter(id__in=list(ids))
        return HouseListingSerializer(houses, many=True).data






