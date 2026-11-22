from django.urls import path
from .views import MyVotingStatus, SubmitVote
urlpatterns = [
    path('elections/<int:pk>/my-status/', MyVotingStatus.as_view()),
    path('elections/<int:pk>/submit-vote/', SubmitVote.as_view()),
]
