from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    # Development-only connectivity check; does not expose database or user information.
    return Response({'status': 'ok'})
