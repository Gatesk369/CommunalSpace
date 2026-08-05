from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin, IsSelfOrAdmin
from .serializers import UserSerializer


# Create your views here.
class UserBaseView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None


class UserListDetailView(UserBaseView):
    def get_permissions(self):
        if self.kwargs.get("pk"):
            return [IsAuthenticated(), IsSelfOrAdmin()]
        return [IsAdmin()]

    def get(self, request, pk=None):
        if pk is None:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(UserBaseView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def put(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(UserBaseView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def delete(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logged out successfully"}, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
