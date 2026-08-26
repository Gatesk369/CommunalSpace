from accounts.permissions import IsBusinessOwnerOrAdmin, IsCommunityAdmin
from django.db.models import Avg, Count
from notifications.models import Notification
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, BusinessBranch, BusinessRating, Follow
from .serializers import (
    BusinessBranchSerializer,
    BusinessRatingSerializer,
    BusinessSerializer,
)


# Create your views here.
class BusinessBaseView(APIView):
    def get_object(self, pk):
        try:
            return Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return None


class BusinessListDetailView(BusinessBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        base_queryset = Business.objects.annotate(
            avg_stars_raw=Avg("ratings__stars"),
            rating_count=Count("ratings", distinct=True),
        )

        if pk is None:
            if request.user.role == "community admin":
                community = request.user.administered_communities.first()
                businesses = base_queryset.filter(community=community)
            else:
                businesses = base_queryset.filter(status=Business.APPROVED)
            serializer = BusinessSerializer(businesses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            business = base_queryset.get(pk=pk)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if business.status != Business.APPROVED and request.user.role not in [
            "admin",
            "community admin",
        ]:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = BusinessSerializer(business)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessApprovalView(APIView):
    permission_classes = [IsCommunityAdmin]

    def get(self, request):
        community = request.user.administered_communities.first()
        if community is None:
            return Response(
                {"detail": " You are not an admin of any community."},
                status=status.HTTP_403_FORBIDDEN,
            )
        businesses = Business.objects.filter(
            community=community, status=Business.PENDING
        )
        serializer = BusinessSerializer(businesses, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found"}, status=status.HTTP_404_NOT_FOUND
            )

        community = request.user.administered_communities.first()
        if community is None or business.community != community:
            return Response(
                {"detail": "Your are not authorized to review this business"},
                status=status.HTTP_403_FORBIDDEN,
            )

        action = request.data.get("action")

        if action == "approve":
            business.status = Business.APPROVED
            business.save()
            first_branch = business.branches.first()
            if first_branch:
                first_branch.status = BusinessBranch.APPROVED
                first_branch.save()
            owner = business.owner
            if owner and owner.role != "business owner":
                owner.role = "business owner"
                owner.save()
            if owner:
                Notification.objects.create(
                    recipient=owner,
                    notification_type=Notification.BUSINESS_APPROVAL,
                    business=business,
                    message=f"Your business '{business.name}' was approved!",
                )
            return Response({"detail": "Business approved."}, status=status.HTTP_200_OK)

        elif action == "reject":
            business.status = Business.REJECTED
            business.rejection_reason = request.data.get("rejection_reason", "")
            business.save()
            first_branch = business.branches.first()
            if first_branch:
                first_branch.status = BusinessBranch.REJECTED
                first_branch.rejection_reason = business.rejection_reason
                first_branch.save()
            if business.owner:
                Notification.objects.create(
                    recipient=business.owner,
                    notification_type=Notification.BUSINESS_APPROVAL,
                    business=business,
                    message=f"Your business '{business.name}' was rejected. Reason: {business.rejection_reason}",
                )
            return Response({"detail": "Business rejected."}, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Invald action. Use 'approve' or 'reject'"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BusinessBranchApprovalView(APIView):
    permission_classes = [IsCommunityAdmin]

    def get(self, request):
        community = request.user.administered_communities.first()
        if community is None:
            return Response(
                {"detail": "You are not an admin of any community."},
                status=status.HTTP_403_FORBIDDEN,
            )
        branches = BusinessBranch.objects.filter(
            community=community, status=BusinessBranch.PENDING
        )
        serializer = BusinessBranchSerializer(branches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            branch = BusinessBranch.objects.get(pk=pk)
        except BusinessBranch.DoesNotExist:
            return Response(
                {"detail": "Branch not found."}, status=status.HTTP_404_NOT_FOUND
            )

        community = request.user.administered_communities.first()
        if community is None or branch.community != community:
            return Response(
                {"detail": "You are not authorized to review this branch."},
                status=status.HTTP_403_FORBIDDEN,
            )

        action = request.data.get("action")

        if action == "approve":
            branch.status = BusinessBranch.APPROVED
            branch.save()
            return Response({"detail": "Branch approved."}, status=status.HTTP_200_OK)

        elif action == "reject":
            branch.status = BusinessBranch.REJECTED
            branch.rejection_reason = request.data.get("rejection_reason", "")
            branch.save()
            return Response({"detail": "Branch rejected."}, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Invalid action. Use 'approve' or 'reject'."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BusinessUpdateView(BusinessBaseView):
    permission_classes = [IsAuthenticated, IsBusinessOwnerOrAdmin]

    def put(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, business)
        serializer = BusinessSerializer(business, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, business)
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessDeleteView(BusinessBaseView):
    permission_classes = [IsAuthenticated, IsBusinessOwnerOrAdmin]

    def delete(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, business)
        business.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RateBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk, status=Business.APPROVED)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        stars = request.data.get("stars")

        try:
            stars = int(stars)
        except (TypeError, ValueError):
            return Response(
                {"detail": "stars must be an integer between 1 and 10."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if stars < 1 or stars > 10:
            return Response(
                {"detail": "stars must be between 1 and 10."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rating, created = BusinessRating.objects.update_or_create(
            business=business,
            user=request.user,
            defaults={"stars": stars},
        )

        return Response(
            BusinessRatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UnrateBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = BusinessRating.objects.filter(
            business_id=pk, user=request.user
        ).delete()

        if not deleted:
            return Response(
                {"detail": "You haven't rated this business."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": "Rating removed."},
            status=status.HTTP_200_OK,
        )


class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk, status=Business.APPROVED)
        except Business.DoesNotExist:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        follow = Follow.objects.filter(follower=request.user, business=business).first()

        if follow:
            follow.delete()
            return Response(
                {"detail": "Unfollowed.", "following": False},
                status=status.HTTP_200_OK,
            )

        Follow.objects.create(follower=request.user, business=business)

        if business.owner:
            Notification.objects.create(
                recipient=business.owner,
                notification_type=Notification.NEW_FOLLOWER,
                business=business,
                message=f"{request.user.first_name} started following {business.name}.",
            )

        return Response(
            {"detail": "Followed.", "following": True},
            status=status.HTTP_201_CREATED,
        )
