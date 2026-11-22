from .models import AuditLog

def record(actor, action, resource_type, resource_id=None):
    # Never log ballot IDs, selections, credentials, or voter submission events.
    return AuditLog.objects.create(actor=actor, action=action,
        resource_type=resource_type, resource_id=resource_id, outcome='SUCCESS')
