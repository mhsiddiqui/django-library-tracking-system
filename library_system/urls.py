from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from library import views
from library.views import ActivityReportView

router = routers.DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'loans', views.LoanViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/members/top-active/', ActivityReportView.as_view()),
    path('api/', include(router.urls)),
]