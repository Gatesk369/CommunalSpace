from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailVerificationToken, PasswordResetToken, User
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
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        refresh_token = request.data.get("refresh")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response(
                {"detail": "Both old and new password are reqiured"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if old_password == new_password:
            return Response(
                {"detail": "New password cannot be the same as old password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class UserVerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = verification_token.user
        user.is_active = True
        user.save()
        verification_token.delete()
        return Response(
            {"detail": "Email verified successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # don't reveal if email exists or not
            return Response(
                {
                    "detail": "If an account with that email exists, a reset link has been sent."
                },
                status=status.HTTP_200_OK,
            )
        token = PasswordResetToken.objects.create(user=user)
        reset_link = f"http://localhost:8000/api/accounts/reset-password/{token.token}/"
        send_mail(
            subject="Reset your CommunalSpace password",
            message=f"Hi {user.first_name},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, ignore this email.\n\nThis link can only be used once.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response(
            {
                "detail": "If an account with that email exists, a reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"detail": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.is_used = True
        reset_token.save()
        return Response(
            {"detail": "Password reset successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )
