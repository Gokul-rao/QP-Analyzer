from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Department, Subject


@login_required(login_url='login')
def home(request):
    return render(request, "qpanalyze/home.html")

def analyze(request):
    return render(request, "qpanalyze/analyze.html")

def abt(request):
    return render(request, "qpanalyze/abt.html")

def abf(request):

    departments = Department.objects.all()
    subjects = []

    # Check if the department code is present in the GET parameters
    if 'department_code' in request.GET:
        department_code = request.GET['department_code']
        subjects = get_subject_by_department(department_code)
        print(subjects)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(subjects, safe=False)

    context = {
        'departments': departments,
        'subjects': subjects,
    }

    return render(request, "qpanalyze/abf.html", context=context)


def get_subject_by_department(department_no):
    subjects = Subject.objects.filter(department__department_code=department_no)
    subject_list = [subject for subject in subjects.values('subject_code', 'subject_name')]

    return subject_list