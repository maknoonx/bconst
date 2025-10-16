from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def system(request):
    return HttpResponse("Hello, Django app is running!")
