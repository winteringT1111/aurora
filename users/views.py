from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from member.models import Character
from users.models import CharInfo
from django.contrib.auth.decorators import login_required
from .models import *


def signup(request):
    all_charac = Character.objects.values_list('name_en', flat=True)
    print(all_charac)
    
    if request.method == "POST":
        commucode = request.POST['commucode']
        print(request.POST['username'])

        if request.POST['password1']==request.POST['password2'] and commucode == "aurorafoederis" and request.POST['username'] in all_charac:
            Newuser = User.objects.create_user(request.POST['username'], password=request.POST['password1'])            
            auth.login(request,Newuser)

            user = request.user
            charac = CharInfo(char=Character.objects.get(name_en=request.POST['username']),
                            user=user,)
            charac.save()

            char=Character.objects.get(name_en=request.POST['username'])
            char.gold = request.POST['gold']
            char.save()
            
            return redirect('main:main_page')
    return render(request,'registration/signup.html')



def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main:main_page')
        else:
            return render(request,'main.html', {'error':'오류입니다'})
    else:
        return render(request,'main.html')