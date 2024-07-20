from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login , logout
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View , UpdateView


class login_view(View):
    def get(self , request):
        form = AuthenticationForm()
        context = {
            'form' : form
        }
        return render(request , 'accounts/login.html' , context)
    
    def post(self , request):
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username , password=password)
                if user is not None:
                    login(request , user)
                    return redirect('index')
        return redirect('index')

class logout_view(View):
    def post(self , request):
        if request.method == 'POST':
            logout(request)
        return redirect('index')
