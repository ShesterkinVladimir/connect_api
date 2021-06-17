from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.OrderListView.as_view()),
    path("orders/<int:pk>/", views.OrderSpecificView.as_view()),
    path("orders/<int:pk>/accept/", views.OrderAccept.as_view()),
    path("orders/<int:pk>/fail/", views.OrderFail.as_view()),
]