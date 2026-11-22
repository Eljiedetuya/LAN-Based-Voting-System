from rest_framework.views import exception_handler

def normalized_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        original = response.data
        response.data = {'error': {'code': getattr(exc, 'default_code', 'request_error'), 'detail': original}}
    return response
