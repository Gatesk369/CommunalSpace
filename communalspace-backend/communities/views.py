from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Community
from .serializers import CommunitySerializer
from rest_framework import status


# Create your views here.
class CommunityBaseView(APIView):
    def get_object(self, pk):
        try:
            return Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return None


class CommunityListDetailView(CommunityBaseView):
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
    def post(self, request):
        serializer = CommunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityUpdateView(CommunityBaseView):
    def put(self, request, pk):
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

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

        serializer = CommunitySerializer(community, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityDeleteView(CommunityBaseView):
    def delete(self, request, pk):
        community = self.get_object(pk)
        if community is None:
            return Response(
                {"detail": "Community not found."}, status=status.HTTP_404_NOT_FOUND
            )

        community.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
