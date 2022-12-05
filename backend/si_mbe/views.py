# from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

# Create your views here.


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
