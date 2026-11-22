from django.urls import path
from .views import (AdminElectionList, AdminElectionDetail, ElectionLifecycle,
    PositionListCreate, PositionDetail, CandidateListCreate, CandidateDetail,
    PublishedElections, PublishedCandidates, EligibilityListCreate, EligibilityBulkPreview, EligibilityBulkAssign)
urlpatterns = [
    path('elections/active/', PublishedElections.as_view()),
    path('elections/<int:pk>/candidates/', PublishedCandidates.as_view()),
    path('admin/elections/', AdminElectionList.as_view()),
    path('admin/elections/<int:pk>/', AdminElectionDetail.as_view()),
    path('admin/elections/<int:pk>/open/', ElectionLifecycle.as_view(), {'action':'open'}),
    path('admin/elections/<int:pk>/close/', ElectionLifecycle.as_view(), {'action':'close'}),
    path('admin/elections/<int:election_id>/positions/', PositionListCreate.as_view()),
    path('admin/positions/<int:pk>/', PositionDetail.as_view()),
    path('admin/candidates/', CandidateListCreate.as_view()),
    path('admin/candidates/<int:pk>/', CandidateDetail.as_view()),
    path('admin/elections/<int:pk>/eligibility/', EligibilityListCreate.as_view()),
    path('admin/elections/<int:pk>/eligibility/bulk/preview/', EligibilityBulkPreview.as_view()),
    path('admin/elections/<int:pk>/eligibility/bulk/', EligibilityBulkAssign.as_view()),
]
