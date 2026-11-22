from django.urls import path
from .views import AuditList
urlpatterns = [path('admin/audit-events/', AuditList.as_view())]
