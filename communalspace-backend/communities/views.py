from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Community, CommunityAdminApplication
from .serializers import CommunitySerializer, CommunityAdminApplicationSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin, IsCommunityAdminOrAdmin


# Create your views here.
class CommunityBaseView(APIView):
    def get_object(self, pk):
        try:
            return Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return None


class CommunityListDetailView(CommunityBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            communities = Community.objects.all()
            serializer = CommunitySerializer(communities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CommunitySerializer(community)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommunityCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = CommunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityUpdateView(CommunityBaseView):
    permission_classes = [IsAuthenticated, IsCommunityAdminOrAdmin]

    def put(self, request, pk):
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, community)
        serializer = CommunitySerializer(community, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, community)
        serializer = CommunitySerializer(community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDeleteView(CommunityBaseView):
    permission_classes = [IsAdmin]

    def delete(self, request, pk):
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

        community.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommunityApplicationSeasonView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            community = Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return Response(
                {"detail": "Community not found"}, status=status.HTTP_404_NOT_FOUND
            )
        action = request.data.get("action")

        if action == "open":
            community.applications_open = True
            community.save()
            return Response(
                {"detail": "Applications are now open."}, status=status.HTTP_200_OK
            )
        elif action == "close":
            community.applications_open = False
            community.save()
            return Response(
                {"detail": "Applications are now closed."}, status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid action. Use 'open' or 'close'."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommunityAdminApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role != "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)
        applications = CommunityAdminApplication.objects.filter(community_id=pk)
        serializer = CommunityAdminApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            community = Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not community.applications_open:
            return Response(
                {"detail": "Applications are not open for this community."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.administered_communities.exists():
            return Response(
                {"detail": "You are already an admin of a community."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        already_applied = CommunityAdminApplication.objects.filter(
            applicant=request.user,
            community=community,
            status=CommunityAdminApplication.PENDING,
        ).exists()
        if already_applied:
            return Response(
                {"detail": "You have already applied to this community."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application = CommunityAdminApplication.objects.create(
            applicant=request.user,
            community=community,
        )
        serializer = CommunityAdminApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommunityAdminApplicationReviewView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk, app_pk):
        try:
            application = CommunityAdminApplication.objects.get(
                pk=app_pk, community_id=pk
            )
        except CommunityAdminApplication.DoesNotExist:
            return Response(
                {"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get("action")

        if application.status != CommunityAdminApplication.PENDING:
            return Response(
                {"detail": "This application has already been reviewed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "approve":
            application.status = CommunityAdminApplication.APPROVED
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.save()

            applicant = application.applicant
            applicant.role = "community admin"
            applicant.save()

            application.community.admins.add(applicant)

            return Response(
                {"detail": "Application approved."}, status=status.HTTP_200_OK
            )

        elif action == "reject":
            application.status = CommunityAdminApplication.REJECTED
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.save()
            return Response(
                {"detail": "Application rejected."}, status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid action. Use 'approve' or 'reject'."},
            status=status.HTTP_400_BAD_REQUEST,
        )
