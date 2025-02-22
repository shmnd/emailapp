from django.contrib.auth import login,logout,authenticate
from authentication.models import Users
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import HttpResponse

class UserRegisterView(View):
    template_name = "admin/authentication/signup.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name)

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, self.template_name)

        Users.objects.create(
            email=email,
            username=username,
            password=make_password(password),  
            is_active=True,
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("authentication:login") 
    

class UserLoginView(View):
    template_name = "admin/authentication/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home:subscribe")  
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name)

class LogoutView(View):
    template_name = "admin/authentication/login.html"
    def get(self, request):
        logout(request)

        response = HttpResponse("You have been logged out.")
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return redirect("authentication:login")
