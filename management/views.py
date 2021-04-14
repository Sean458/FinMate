from django.db.models import *

from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .models import Category, Transaction, CustomUser
from django.http import JsonResponse
import json

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Create your views here.


def home(request):
    return render(request, 'home.html')


def index(request):
    dataset = Transaction.objects.raw('SELECT distinct(id), sum(amount) as total_amount,date FROM management_transaction GROUP BY id ORDER BY id')
    dataset2=Transaction.objects.raw('SELECT management_transaction.id,management_transaction.user_id, management_transaction.amount ,management_category.category_name FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=1')
    dataset3=Transaction.objects.raw('SELECT management_transaction.id,management_transaction.user_id, management_transaction.amount ,management_category.category_name FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=0')
    ctry =CustomUser.objects.raw('SELECT user_id,country from management_customuser')
      #  .values('VehicleID') \
      #  .annotate(hours_count=sum('hours'),amount_count=sum('total')) \
      #  .group_by('VehicleID') \
      #  .order_by('VehicleID')    

    usd=request.user.id

    categories = list()
    date_series = list()
    amount_series = list()
    expense_series=list()
    income_series=list()

    ind=0
    usa=0
    uk=0
    china=0
    cnt=0
    for i in ctry:
        #print('country',i.country)
        if i.country=='India':
            ind+=1
            cnt+=1
        if i.country=='USA':
            usa+=1
            cnt+=1
        if i.country=='UK':
            uk+=1
            cnt+=1
        if i.country=='China':
            china+=1
            cnt+=1
    
    ind=int((ind/cnt)*100)
    usa=int((usa/cnt)*100)
    uk=int((uk/cnt)*100)
    china=int((china/cnt)*100)
    #print(ind,usa,uk,china)
    
       
    for entry in dataset:
        uid = Transaction.objects.get(pk=entry.id)
        name = uid.user_id
        if name==usd:
            amount_series.append((int)(entry.total_amount))

    for entry in dataset2:
        
        uid=Transaction.objects.get(pk=entry.id)
        amount=uid.amount
        name = uid.user_id
        
        if name==usd:
            
            categories.append('%s' % name)
            expense_series.append((int)(entry.amount))

    for entry in dataset3:
        
        uid=Transaction.objects.get(pk=entry.id)
        amount=uid.amount
        name = uid.user_id
        
        if name==usd:
            
            categories.append('%s' % name)
            income_series.append((int)(entry.amount))
    
    
    
    
    arr=[]
    
    income=Transaction.objects.raw('SELECT management_transaction.id,sum(management_transaction.amount) as amount  FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=0 and management_transaction.user_id=%s',[usd])
    for i in income:
        arr.append(i.amount)
        
    expenses=Transaction.objects.raw('SELECT management_transaction.id,sum(management_transaction.amount) as amount FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=1 and management_transaction.user_id=%s',[usd])
    for i in expenses:
        arr.append(i.amount)
    if arr[0]!=None and arr[1]!=None:
        savings=arr[0]-arr[1]
    else:
        savings=None
    

    return render(request, 'index.html',{'income': income,'expenses': expenses,'savings': savings,'categories': json.dumps(categories),
        #'date_series': json.dumps(date_series),
        'amount_series': json.dumps(amount_series),
        'expense_series': json.dumps(expense_series),
        'income_series': json.dumps(income_series),
        'ind':ind,
        'usa':usa,
        'uk':uk,
        'china':china,})



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
            return redirect("/index")
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
    #print(category_list)
    return render(request, "category_income.html", {'category_list': category_list})


def category_expense(request):
    category_list = Category.objects.filter(user=request.user, is_expense=True)
    #print(category_list)
    return render(request, "category_expense.html", {'category_list': category_list})


def save_data(request):
    if request.method == "POST":
        categoryid = request.POST.get('categoryid')
        categorytype = request.POST.get('ctype')
        #print(categorytype)
        #print(categoryid)
        category = request.POST.get('category')
        #print(category)
        #print(request.user)
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
        #print(category_data)
        return JsonResponse({'status': 'Save', 'category_data': category_data})


def delete_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        #print(cid)
        category = Category.objects.get(pk=cid)
        category.delete()
        return JsonResponse({'status': 1})


def edit_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        #print(cid)
        category = Category.objects.get(pk=cid)
        category_data = {"cid": category.id,
                         "category_name": category.category_name}
        return JsonResponse(category_data)


def addincome(request):
    category_list = Category.objects.filter(
        user=request.user, is_expense=False)
    return render(request, "addtransaction.html", {'category_list': category_list, 'title': 'Income'})


def addexpense(request):
    category_list = Category.objects.filter(
        user=request.user, is_expense=True)
    return render(request, "addtransaction.html", {'category_list': category_list, 'title': 'Expense'})


def transaction(request):
    if request.method == "POST":
        catid = request.POST.get('catid')
        #print(catid)
        catobj = Category.objects.get(pk=catid)
        amount = request.POST.get('amount')
        #print(amount)
        date = request.POST.get('date')
        #print(date)
        feedback = request.POST.get('feedback')
        #print(feedback)

        new_words = {'cushiony': 1, 'comfort': 0, 'support': 0, 'unsupportive': -1, 'lightweight': 1, 'heavyweight': -1, 'stabilize': 1, 'instability': -1, 'unresponsive': -1, 'durable': 1, 'breathable': 1, 'protective': 1, 'too': 0, 'flimsy': -1, 'freedom': 0, 'tore': -1.5, 'narrow': -1, 'strike': 0, 'right': 1.5, 'hole': -1.5, 'never': -.5,
                     'holes': -1.5, "stiff": -1, 'return': -.5, 'returning': -.5, 'issue': -1, "untied": -1, 'clunky': -1, 'stiffness': -1, 'swollen': -1, 'stylish': 1, 'rip': -1, 'returned': -.5, 'bulky': -1}  # this list specifies sentiment scores for common words that are related to running shoes, in other words it adds context to the sentiment analysis
        sid = SentimentIntensityAnalyzer()
        # updates the lexicon with the specified sentiment scores
        sid.lexicon.update(new_words)
        # calculates the positive, negative, neutral, and compound sentiment score for the review
        score = sid.polarity_scores(feedback)
        #print("Score", score)
        compound = score.get('compound')
        #print("compound", compound)

        newtransaction = Transaction(
            user=request.user, category=catobj, amount=amount, date=date, feedback=feedback, sentiment=compound)

        newtransaction.save()
        return redirect('/transaction')
    else:

        dataset1 = Transaction.objects.raw(
            'SELECT distinct(id), user_id,feedback FROM management_transaction ')

        
        review = list()
        for entry in dataset1:
            usid = Transaction.objects.get(pk=entry.id)
            fdb = usid.feedback
            #print(fdb)
            review.append('%s' % fdb)
        #print(review)
        total = 0
        for i in review:
            #print(i)
            new_words = {'cushiony': 1, 'comfort': 0, 'support': 0, 'unsupportive': -1, 'lightweight': 1, 'heavyweight': -1, 'stabilize': 1, 'instability': -1, 'unresponsive': -1, 'durable': 1, 'breathable': 1, 'protective': 1, 'too': 0, 'flimsy': -1, 'freedom': 0, 'tore': -1.5, 'narrow': -1, 'strike': 0, 'right': 1.5, 'hole': -1.5, 'never': -.5,
                         'holes': -1.5, "stiff": -1, 'return': -.5, 'returning': -.5, 'issue': -1, "untied": -1, 'clunky': -1, 'stiffness': -1, 'swollen': -1, 'stylish': 1, 'rip': -1, 'returned': -.5, 'bulky': -1}  # this list specifies sentiment scores for common words that are related to running shoes, in other words it adds context to the sentiment analysis
            sid = SentimentIntensityAnalyzer()
            # updates the lexicon with the specified sentiment scores
            sid.lexicon.update(new_words)
            # calculates the positive, negative, neutral, and compound sentiment score for the review
            score = sid.polarity_scores(i)
            #print("Score", score)
            compound = score.get('compound')
            #print("compound", compound)

            total += compound
            #print(total)
        alltransaction = Transaction.objects.filter(user=request.user)
        if total < -0.2:

            return render(request, 'addtransaction.html', {'alert_flag': True})
        else:

            return render(request, "transaction.html", {'alltransaction': alltransaction})



