from django.urls import path
from .views import ElectionResults, ElectionReportCSV
urlpatterns = [
    path('results/<int:pk>/', ElectionResults.as_view()),
    path('reports/<int:pk>/csv/', ElectionReportCSV.as_view()),
]
