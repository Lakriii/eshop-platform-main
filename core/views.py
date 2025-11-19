from django.shortcuts import render
# Home view
def home(request):
    return render(request, "core/home.html")
