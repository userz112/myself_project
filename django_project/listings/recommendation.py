import random,math
from collections import defaultdict
from typing import List,Dict,Tuple,Any,Set,Iterator
from django.db.models import QuerySet
from .models import HouseListing,FavoriteHouse
from .serializers import HouseListingSerializer

class RecommendationEngine:
    def __init__(self, user_id, house_listings=None):
        self.user_id = user_id
        self.room_weight = 0.3
        self.size_weight = 0.3
        self.floor_weight = 0.2
        self.position_weight = 0.2

    def find_recommendations(self):
        favorite_ids = FavoriteHouse.objects.filter(user_id=self.user_id).values_list('house_listing_id', flat=True)
        if not favorite_ids:
            return []

        fav_houses = HouseListing.objects.filter(id__in=list(favorite_ids))

        price_list = [h.total_price for h in fav_houses]
        city_num_dic = defaultdict(int)
        for h in fav_houses:
            city_num_dic[h.city] += 1

        max_price = max(price_list)
        min_price = min(price_list)
        most_city = max(city_num_dic, key=city_num_dic.get)

        qs = HouseListing.objects.filter(
            city=most_city,
            total_price__gte=min_price * 0.7,
            total_price__lte=max_price * 1.3,
        ).exclude(id__in=list(favorite_ids))

        fav_types = list(set(h.house_type for h in fav_houses))
        fav_sizes = list(set(h.house_size for h in fav_houses))
        fav_floors = list(set(h.house_height for h in fav_houses))
        fav_positions = list(set(h.house_position for h in fav_houses))

        scored = []
        for h in qs:
            score = 0
            if h.house_type in fav_types:
                score += self.room_weight
            if h.house_size in fav_sizes:
                score += self.size_weight
            if h.house_height in fav_floors:
                score += self.floor_weight
            if h.house_position in fav_positions:
                score += self.position_weight
            scored.append((h, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_houses = [item[0] for item in scored[:3]]
        return HouseListingSerializer(top_houses, many=True).data
