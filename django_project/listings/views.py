from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import HouseListingSerializer,FavoriteHouseSerializer
from .models import HouseListing,FavoriteHouse
from .recommendation import RecommendationEngine



class DisplayHouseView(APIView):
    permission_classes = [AllowAny]

    query_rules = {
        'city': 'city__icontains',
        'max_size': 'house_size__lte',
        'min_size': 'house_size__gte',
        'max_unit_price': 'unit_price__lte',
        'min_unit_price': 'unit_price__gte',
    }

    def get(self,request):
        # 过滤空值
        filter_params = {
            'city': request.GET.get('city'),
            'max_size': int(request.GET.get('max_size')) if request.GET.get('max_size') else None,
            'min_size': int(request.GET.get('min_size')) if request.GET.get('min_size') else None,
            'max_unit_price': float(request.GET.get('max_unit_price')) if request.GET.get('max_unit_price') else None,
            'min_unit_price': float(request.GET.get('min_unit_price')) if request.GET.get('min_unit_price') else None,
        }

        filter = {}

        for k,filter_val in filter_params.items():
            if filter_val:
                filter[self.query_rules[k]] = filter_val

        if not filter:
            filter = None
        if filter is not None:
            queryset = HouseListing.objects.filter(**filter).order_by('-created_time')
        else:
            queryset = HouseListing.objects.all().order_by('-created_time')
        paginator = Paginator(queryset, 15) # 每页15条
        page = request.GET.get('page', 1) # `page`参数默认值为1
        houses = paginator.get_page(page)
        serializer = HouseListingSerializer(houses, many=True)
        return JsonResponse({
            'houses': serializer.data,
            'total': paginator.count,
            'page': houses.number,
            'pages': paginator.num_pages,
        })

class FavoriteHouseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = FavoriteHouseSerializer()
        favorites = serializer.check_user_favorites(request.user.id)
        return JsonResponse(favorites, safe=False)

    def post(self, request):
        print(request.data)
        house_listing_id = request.data.get('house_id')
        if not house_listing_id:
            return JsonResponse({'error': '房源ID缺失'}, status=400)
        if FavoriteHouse.objects.filter(user_id=request.user.id, house_listing_id=house_listing_id).exists():
            FavoriteHouse.objects.filter(user_id=request.user.id, house_listing_id=house_listing_id).delete()
            return JsonResponse({'msg': '已取消收藏'}, status=200)
        FavoriteHouse.objects.create(user_id=request.user.id, house_listing_id=house_listing_id)
        return JsonResponse({'msg': '收藏成功'}, status=200)

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = RecommendationEngine(request.user.id)
        result = engine.find_recommendations()
        return JsonResponse(result, safe=False)



