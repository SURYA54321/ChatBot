from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer


class RegisterView(APIView):
    # >>> IMPORTANT: overrides the global default
    # (IsAuthenticated, set in config/settings.py) — without this,
    # nobody could ever reach this endpoint to create their first
    # account.
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # >>> NEW: issue tokens immediately so the frontend can log
        # the user straight in after registering, instead of making
        # a second round-trip to /auth/token/.
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )