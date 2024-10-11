from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def home(request):
    return render(request, "qpanalyze/home.html")

def analyze(request):
    return render(request, "qpanalyze/analyze.html")

def abt(request):
    return render(request, "qpanalyze/abt.html")

def abf(request):
    return render(request, "qpanalyze/abf.html")