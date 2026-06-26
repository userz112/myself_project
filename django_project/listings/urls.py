from django.urls import path
from . import views

urlpatterns = [
    path('houses/', views.DisplayHouseView.as_view(), name='display_houses'),
    path('favorites/', views.FavoriteHouseView.as_view(), name='favorites'),
    path('recommendations/', views.RecommendationView.as_view(), name='recommendations'),
]
    
