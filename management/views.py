from django.db.models import *

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .models import Category, Transaction
from django.http import JsonResponse


# Create your views here.
def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        username = request.POST['userName']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        if password != confirmPassword:
            # messages.warning(request, "Passwords do not match. Try again")
            return redirect('/users/register')
        else:
            if User.objects.filter(username=username).exists():
                # messages.warning(
                #     request, "Username is taken. Try another Username")
                return redirect('/users/register')
            elif User.objects.filter(email=email).exists():

                # messages.warning(request, "Email is taken. Try another Email")
                return redirect('/users/register')
            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email, first_name=firstName, last_name=lastName)
                user.save()
                # messages.success(request, "Registration Successful!")
                return redirect("/users/login")

    else:
        return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, "Logged In Successfuly!")
            return redirect("/")
        else:
            # messages.warning(request, "Invalid Credentials")
            return redirect('/users/login')
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    # messages.info(request, "Logged Out")
    return redirect("/")


def category_income(request):
    category_list = Category.objects.filter(
        user=request.user, is_expense=False)
    print(category_list)
    return render(request, "category_income.html", {'category_list': category_list})


def category_expense(request):
    category_list = Category.objects.filter(user=request.user, is_expense=True)
    print(category_list)
    return render(request, "category_expense.html", {'category_list': category_list})


def save_data(request):
    if request.method == "POST":
        categoryid = request.POST.get('categoryid')
        categorytype = request.POST.get('ctype')
        print(categorytype)
        print(categoryid)
        category = request.POST.get('category')
        print(category)
        print(request.user)
        if categoryid != '':
            if categorytype == 'income':
                newcategory = Category(
                    id=categoryid, user=request.user, category_name=category, is_expense=False)
            else:
                newcategory = Category(
                    id=categoryid, user=request.user, category_name=category, is_expense=True)
        else:
            if categorytype == 'income':
                newcategory = Category(
                    user=request.user, category_name=category, is_expense=False)
            else:
                newcategory = Category(
                    user=request.user, category_name=category, is_expense=True)

        newcategory.save()
        if categorytype == 'income':
            cat = Category.objects.filter(
                user=request.user, is_expense=False).values()
        else:
            cat = Category.objects.filter(
                user=request.user, is_expense=True).values()
        category_data = list(cat)
        print(category_data)
        return JsonResponse({'status': 'Save', 'category_data': category_data})


def delete_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        print(cid)
        category = Category.objects.get(pk=cid)
        category.delete()
        return JsonResponse({'status': 1})


def edit_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        print(cid)
        category = Category.objects.get(pk=cid)
        category_data = {"cid": category.id,
                         "category_name": category.category_name}
        return JsonResponse(category_data)
