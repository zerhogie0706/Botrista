from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import LoginSerializer
from .decorators import login_required


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def test(request):
    return JsonResponse({'success': True})
