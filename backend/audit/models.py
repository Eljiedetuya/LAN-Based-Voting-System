from django.conf import settings
from django.db import models

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=64)
    resource_type = models.CharField(max_length=32)
    resource_id = models.PositiveBigIntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=12, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at'], name='idx_audit_time')]
