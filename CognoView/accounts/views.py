from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.
# @login_required(login_url='login')
def HomePage(request):
    return render (request,'accounts/home2.html')

def SignupPage(request):
    if request.method=='POST':
        name=request.POST.get('name')
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:
            my_user=User.objects.create_user(name,uname,email,pass1)
            my_user.save()
            return redirect('login')
        


    return render (request,'accounts/pages-register.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'accounts/pages-login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

def question_cat(request):
    return render(request,"qpanalyze/genquestions.html")

def report(request):
    return render(request,"qpanalyze/report.html")
