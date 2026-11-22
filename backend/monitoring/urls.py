from django.urls import path
from .views import ParticipationSummary, SystemHealth, MonitorElectionList, ElectionIntegritySummary
urlpatterns = [
    path('monitoring/elections/', MonitorElectionList.as_view()),
    path('monitoring/integrity/<int:pk>/', ElectionIntegritySummary.as_view()),
    path('monitoring/participation/', ParticipationSummary.as_view()),
    path('monitoring/health/', SystemHealth.as_view()),
]
