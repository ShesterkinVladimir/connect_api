from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", views.OrderSpecificView.as_view(), name="order_pk"),
    path("orders/<int:pk>/accept/", views.OrderAccept.as_view(), name="accept"),
    path("orders/<int:pk>/fail/", views.OrderFail.as_view(), name="fail"),
]