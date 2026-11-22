from django.urls import path
from .views import (CSRFView, LoginView, LogoutView, MeView, PasswordChangeView,
    StudentListCreateView, StudentDetailView, StaffAccountListCreateView)
urlpatterns = [
    path('auth/csrf/', CSRFView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/me/', MeView.as_view()),
    path('auth/password/change/', PasswordChangeView.as_view()),
    path('admin/voters/', StudentListCreateView.as_view()),
    path('admin/voters/<int:pk>/', StudentDetailView.as_view()),
    path('admin/staff/', StaffAccountListCreateView.as_view()),
]
