from functools import wraps
from rest_framework.authtoken.models import Token
from django.http import JsonResponse


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Extract the token from the Authorization header
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                token = Token.objects.get(key=token)
                request.user = token.user  # Attach the user to the request
            except Token.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Token missing'}, status=401)

        return view_func(request, *args, **kwargs)
    
    return wrapped_view
