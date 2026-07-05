from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Business
from .serializers import BusinessSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsCommunityAdmin, IsBusinessOwnerOrAdmin


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
        if pk is None:
            if request.user.role == "community admin":
                community = request.user.administered_communities.first()
                businesses = Business.objects.filter(community=community)
            else:
                businesses = Business.objects.filter(status=Business.APPROVED)
            serializer = BusinessSerializer(businesses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        business = self.get_object(pk)
        if business is None:
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
            owner = business.owner
            if owner and owner.role != "business owner":
                owner.role = "business owner"
                owner.save()
            return Response({"detail": "Business approved."}, status=status.HTTP_200_OK)

        elif action == "reject":
            business.status = Business.REJECTED
            business.rejection_reason = request.data.get("rejection_reason", "")
            business.save()
            return Response({"detail": "Business rejected."}, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Invald action. Use 'approve' or 'reject'"},
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
