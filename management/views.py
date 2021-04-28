from django.db.models import *

from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from .models import Category, Notification, Transaction, CustomUser
from django.http import JsonResponse, HttpResponse
import json

from django.utils.dateparse import parse_date
import datetime
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer


import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

# Create your views here.


def home(request):
    return render(request, 'home.html')


def index(request):
    if request.user.is_authenticated:
        usd = request.user.id

        dataset = Transaction.objects.raw(
            'SELECT distinct(management_transaction.id), sum(management_transaction.amount) as total_amount,date,management_category.category_name FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id  GROUP BY management_transaction.id ORDER BY management_transaction.id')
        # print(dataset)
        dataset2 = Transaction.objects.raw(
            'SELECT management_transaction.id,management_transaction.user_id, sum(management_transaction.amount) as total_expense,management_transaction.date ,management_category.category_name FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=1  group by management_transaction.date order by management_transaction.date')
        dataset3 = Transaction.objects.raw(
            'SELECT management_transaction.id,management_transaction.user_id, sum(management_transaction.amount) as total_income ,management_transaction.date,management_category.category_name FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=0 group by management_transaction.date order by management_transaction.date')
        ctry = CustomUser.objects.raw(
            'SELECT user_id,country from management_customuser')
        #  .values('VehicleID') \
        #  .annotate(hours_count=sum('hours'),amount_count=sum('total')) \
        #  .group_by('VehicleID') \
        #  .order_by('VehicleID')
        #usd = request.user.id
        c = CustomUser.objects.raw(
            'SELECT user_id from management_customuser where user_id=%s', [usd])
        # print(c)
        percentile = 0.0
        for entry in c:
            # print(entry.user_id)
            queryset = CustomUser.objects.all()
            total_count = queryset.count()
            if total_count:
                percentile = float(queryset.filter(
                    credit_score__lt=entry.credit_score).count())/total_count
                # print(percentile)
            else:
                percentile = 0.0
            # print('percentile',percentile)
        percentile = percentile*100

        categories = list()
        date_series = list()
        date_series_inc = list()
        amount_series = list()
        expense_series = list()
        income_series = list()

        ind = 0
        usa = 0
        uk = 0
        china = 0
        cnt = 0
        for i in ctry:
            # print('country',i.country)
            if i.country == 'India':
                ind += 1
                cnt += 1
            if i.country == 'USA':
                usa += 1
                cnt += 1
            if i.country == 'UK':
                uk += 1
                cnt += 1
            if i.country == 'China':
                china += 1
                cnt += 1

        ind = int((ind/cnt)*100)
        usa = int((usa/cnt)*100)
        uk = int((uk/cnt)*100)
        china = int((china/cnt)*100)
        # print(ind, usa, uk, china)

        for entry in dataset:
            # print(entry.id, entry.total_amount, entry.date)
            uid = Transaction.objects.get(pk=entry.id)
            name = uid.user_id
            if name == usd:
                amount_series.append(
                    [entry.category_name, (int)(entry.total_amount)])
                # print(amount_series)
        # print(json.dumps(amount_series))
        cut = 0
        for entry in dataset2:

            uid = Transaction.objects.get(pk=entry.id)
            amount = uid.amount
            name = uid.user_id
            #cat_id = uid.category
            #cat_or_id = Category.objects.get(pk = cat_id)
            #cat_name = cat_or_id.category_name
            if name == usd and cut != 5:
                date_series.append((str)(entry.date))
                expense_series.append((int)(entry.total_expense))
                cut += 1
                # print(expense_series)
        cuti = 0
        for entry in dataset3:

            uid = Transaction.objects.get(pk=entry.id)
            amount = uid.amount
            name = uid.user_id

            if name == usd and cuti != 5:
                date_series_inc.append((str)(entry.date))
                income_series.append((int)(entry.total_income))
                cuti += 1

        arr = []

        income = Transaction.objects.raw(
            'SELECT management_transaction.id,sum(management_transaction.amount) as amount  FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=0 and management_transaction.user_id=%s', [usd])
        for i in income:
            arr.append(i.amount)
            # print(arr)

        expenses = Transaction.objects.raw(
            'SELECT management_transaction.id,sum(management_transaction.amount) as amount FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=1 and management_transaction.user_id=%s', [usd])
        for i in expenses:
            arr.append(i.amount)
            # print(arr)

        if arr[0] != None and arr[1] != None:
            savings = arr[0]-arr[1]
        else:
            savings = None

        print(categories)
        print(date_series)
        print(date_series_inc)
        print(amount_series)
        print(expense_series)
        print(income_series)

        return render(request, 'index.html', {'income': income, 'expenses': expenses, 'savings': savings, 'categories': json.dumps(categories),
                                              'date_series': json.dumps(date_series),
                                              'date_series_inc': json.dumps(date_series_inc),
                                              'amount_series': json.dumps(amount_series),
                                              'expense_series': json.dumps(expense_series),
                                              'income_series': json.dumps(income_series),
                                              'ind': ind,
                                              'usa': usa,
                                              'uk': uk,
                                              'china': china,
                                              'percentile': percentile, })
    else:
        return redirect('/users/login')


def register(request):
    if request.method == 'POST':
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        username = request.POST['userName']
        country = request.POST['country']
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
                cust = CustomUser(user_id=user.id, country=country)
                cust.save()

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
    # print(category_list)
    return render(request, "category_income.html", {'category_list': category_list})


def category_expense(request):
    category_list = Category.objects.filter(user=request.user, is_expense=True)
    # print(category_list)
    return render(request, "category_expense.html", {'category_list': category_list})


def save_data(request):
    if request.method == "POST":
        categoryid = request.POST.get('categoryid')
        categorytype = request.POST.get('ctype')
        # print(categorytype)
        # print(categoryid)
        category = request.POST.get('category')
        # print(category)
        # print(request.user)
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
        # print(category_data)
        return JsonResponse({'status': 'Save', 'category_data': category_data})


def delete_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        # print(cid)
        category = Category.objects.get(pk=cid)
        category.delete()
        return JsonResponse({'status': 1})


def edit_data(request):
    if request.method == "POST":
        cid = request.POST.get('cid')
        # print(cid)
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
    cat = 0
    if request.method == "POST":
        catid = request.POST.get('catid')
        cat = catid
        catobj = Category.objects.get(pk=catid)
        cat_name = str(catobj)
        # print(cat_name)
        cat_name = cat_name[4:]
        # print('cat_name', cat_name[4:])
        amount = request.POST.get('amount')
        # print(amount)
        date = request.POST.get('date')
        # print(date)
        description = request.POST.get('description')
        feedback = request.POST.get('feedback')
        # print(feedback)
        if catobj.is_expense == 0:
            feedback = ""

        new_words = {'cushiony': 1, 'comfort': 0, 'support': 0, 'unsupportive': -1, 'lightweight': 1, 'heavyweight': -1, 'stabilize': 1, 'instability': -1, 'unresponsive': -1, 'durable': 1, 'breathable': 1, 'protective': 1, 'too': 0, 'flimsy': -1, 'freedom': 0, 'tore': -1.5, 'narrow': -1, 'strike': 0, 'right': 1.5, 'hole': -1.5, 'never': -.5,
                     'holes': -1.5, "stiff": -1, 'return': -.5, 'returning': -.5, 'issue': -1, "untied": -1, 'clunky': -1, 'stiffness': -1, 'swollen': -1, 'stylish': 1, 'rip': -1, 'returned': -.5, 'bulky': -1}  # this list specifies sentiment scores for common words that are related to running shoes, in other words it adds context to the sentiment analysis
        sid = SentimentIntensityAnalyzer()
        # updates the lexicon with the specified sentiment scores
        sid.lexicon.update(new_words)
        # calculates the positive, negative, neutral, and compound sentiment score for the review
        score = sid.polarity_scores(feedback)
        print("Score", score)
        compound = score.get('compound')
        print("compound", compound)

        usd = request.user.id

        newtransaction = Transaction(
            user=request.user, category=catobj, amount=amount, date=date, description=description, feedback=feedback, sentiment=compound)

        newtransaction.save()

        usd = request.user.id
        print('cat', cat)
        dataset1 = Transaction.objects.raw(
            'select id,category_id,feedback from management_transaction where user_id=%s and category_id=%s', [usd, cat])

        review = list()
        for entry in dataset1:
            usid = Transaction.objects.get(pk=entry.id)
            fdb = usid.feedback
            print(fdb)
            review.append('%s' % fdb)
        print(review)
        total = 0
        for i in review:
            # print(i)
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
            print(total)

        avgtotal = total/(len(review))
        print(avgtotal)

        alltransaction = Transaction.objects.filter(user=request.user)
        if total < -0.2:
            notification = Notification(user=request.user, category=catobj)
            notification.save()
            return render(request, 'transaction.html', {'alert_flag': True, 'cat_name': cat_name,
                                                        'alltransaction': alltransaction})

        arr = []

        income = Transaction.objects.raw(
            'SELECT management_transaction.id,sum(management_transaction.amount) as amount  FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=0 and management_transaction.user_id=%s', [usd])
        for i in income:
            print(i.amount)
            arr.append(i.amount)

        expenses = Transaction.objects.raw(
            'SELECT management_transaction.id,sum(management_transaction.amount) as amount FROM management_transaction INNER JOIN management_category ON management_transaction.category_id=management_category.id WHERE management_category.is_expense=1 and management_transaction.user_id=%s', [usd])
        for i in expenses:
            print(i.amount)
            arr.append(i.amount)

        print(arr)
        if arr[0] != None and arr[1] != None:
            savings = arr[0]-arr[1]
        else:
            savings = None

        cred_score = savings/arr[0]
        print('credscore', cred_score)
        cust = CustomUser.objects.get(user_id=request.user.id)
        cust.credit_score = cred_score

        cust.save(update_fields=['credit_score'])

        return redirect('/transaction')
    else:
        # print(request.GET)
        # print(request.GET.get('startdate'))
        # print(request.GET.get('enddate'))
        # print(type(request.GET.get('startdate')))
        # print(type(request.GET.get('enddate')))
        # startdate = parse_date(request.GET.get('startdate'))
        # enddate = parse_date(request.GET.get('enddate'))
        # startdate = request.GET.get('startdate')
        # enddate = request.GET.get('enddate')
        # print(type(startdate))
        # print(type(enddate))
        # print(startdate)
        # print(enddate)
        alltransaction = Transaction.objects.filter(
            user=request.user).order_by('-id')
        # print(alltransaction)
        return render(request, "transaction.html", {'alltransaction': alltransaction})


def export(request):
    if request.method == "POST":
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        print(startdate)
        print(enddate)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Expenses' + \
            str(datetime.datetime.now())+'.csv'

        writer = csv.writer(response)
        writer.writerow(['Category', 'Amount', 'Date', 'Description'])

        transactions = Transaction.objects.filter(
            user=request.user, date__range=[startdate, enddate])

        for transaction in transactions:
            writer.writerow([transaction.category.category_name, transaction.amount,
                             transaction.date, transaction.description])

        return response
    else:
        return render(request, "export.html")


def report(request):
    if request.method == "POST":
        monthyear = request.POST.get('month')
        print(type(monthyear))
        splitstr = monthyear.split('-')
        year = splitstr[0]
        month = splitstr[1]
        print(year)
        print(type(year))
        print(month)
        print(type(month))

        transobj = Transaction.objects.filter(date__year__gte=year,
                                              date__month__gte=month,
                                              date__year__lte=year,
                                              date__month__lte=month, user=request.user)

        income = 0
        expense = 0

        for i in transobj:
            if i.category.is_expense:
                expense += i.amount
            else:
                income += i.amount

        print(income)
        print(expense)

        saving = income-expense
        print(saving)

        print(transobj)

        template_path = 'report.html'
        context = {'income': income, 'expense': expense,
                   'saving': saving, 'date': monthyear, 'transobj': transobj}
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="report.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        return render(request, "monthly_report.html")
