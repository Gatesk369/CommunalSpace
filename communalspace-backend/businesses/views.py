from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Business
from .serializers import BusinessSerializer
from rest_framework import status


# Create your views here.
class BusinessListCreateView(APIView):
    def get(self, request):
        businesses = Business.objects.all()
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessDetailView(APIView):
    def get_object(self, pk):
        try:
            return Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return None

    def get(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BusinessSerializer(business)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

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

        serializer = BusinessSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        business = self.get_object(pk)
        if business is None:
            return Response(
                {"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND
            )

        business.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
