from django.urls import path
from .views import OptimalRouteView, RouteFormView

urlpatterns = [
    path('', RouteFormView.as_view(), name='route-form'),
    path('route/', OptimalRouteView.as_view(), name='optimal-route'),
]
