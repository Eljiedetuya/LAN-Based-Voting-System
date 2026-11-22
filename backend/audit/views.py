from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from core.permissions import IsAdmin
from .models import AuditLog
from rest_framework import serializers

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'actor_id', 'action', 'resource_type', 'resource_id', 'outcome', 'created_at']

class AuditPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuditList(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AuditLogSerializer
    pagination_class = AuditPagination
    queryset = AuditLog.objects.all().order_by('-created_at')
