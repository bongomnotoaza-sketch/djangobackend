from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Updates
from .serializers import UpdatesSerializer,UpdatesGetSerializer


class UpdatesView(APIView):

    def post(self, request):
        serializer = UpdatesSerializer(data=request.data)

        if serializer.is_valid():
            update = serializer.save()

            return Response(
                UpdatesSerializer(update).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class UpdatesGetView(APIView):

    def get(self, request):
        updates = Updates.objects.all().order_by("-senddate")

        serializer = UpdatesGetSerializer(updates, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )