from django.shortcuts import render

def home(request):
    return render(request, 'website/home.html')

def studio(request):
    return render(request, 'website/studio.html')

def coming_soon(request):
    return render(request, 'website/coming-soon.html')