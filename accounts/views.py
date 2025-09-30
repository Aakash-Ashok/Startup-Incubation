from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Redirect based on role
                if user.role == 'STARTUP':
                    return redirect('startup_dashboard')
                elif user.role == 'FREELANCER':
                    return redirect('freelancer_dashboard')
                elif user.role == 'MENTOR':
                    return redirect('mentor_dashboard')
                elif user.role == 'INVESTOR':
                    return redirect('investor_dashboard')
                else:
                    return redirect('admin:index')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
