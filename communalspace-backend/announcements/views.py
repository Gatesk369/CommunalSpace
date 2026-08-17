from accounts.permissions import IsCommunityAdminOrAdmin
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement
from .serializers import AnnouncementSerializer


def _administers_all_communities(user, communities):
    """Return whether a community admin manages every supplied community."""
    administered_ids = set(user.administered_communities.values_list("id", flat=True))
    community_ids = {community.id for community in communities}
    return community_ids.issubset(administered_ids)


# Create your views here.
class AnnouncementCreateView(APIView):
    permission_classes = [IsCommunityAdminOrAdmin]

    def post(self, request):
        user = request.user

        serializer = AnnouncementSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        requested_communities = serializer.validated_data["communities"]

        if user.role == "community admin" and not _administers_all_communities(
            user, requested_communities
        ):
            return Response(
                {
                    "detail": "You can only send announcements to communities you administer"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        announcement = serializer.save()

        return Response(
            AnnouncementSerializer(announcement).data,
            status=status.HTTP_201_CREATED,
        )


class AnnouncementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        announcements = Announcement.objects.all()
        announcements = announcements.distinct().order_by("-created_at")
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return Response(
                {"detail": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AnnouncementSerializer(announcement)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnnouncementDeleteView(APIView):
    permission_classes = [IsCommunityAdminOrAdmin]

    def delete(self, request, pk):
        user = request.user
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return Response(
                {"detail": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if user.role == "community admin" and not _administers_all_communities(
            user, announcement.communities.all()
        ):
            return Response(
                {
                    "detail": "You cannot delete an announcement that is from a community you do not administer."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnnouncementUpdateView(APIView):
    permission_classes = [IsCommunityAdminOrAdmin]

    def patch(self, request, pk):
        user = request.user
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return Response(
                {"detail": "Announcement not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.role == "community admin" and not _administers_all_communities(
            user, announcement.communities.all()
        ):
            return Response(
                {
                    "detail": "You cannot edit an announcement that is from a community you do not administer."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AnnouncementSerializer(
            announcement,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_communities = serializer.validated_data.get(
            "communities", announcement.communities.all()
        )
        if user.role == "community admin" and not _administers_all_communities(
            user, updated_communities
        ):
            return Response(
                {
                    "detail": "You can only assign announcements to communities you administer."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        announcement = serializer.save()
        return Response(
            AnnouncementSerializer(announcement).data,
            status=status.HTTP_200_OK,
        )
