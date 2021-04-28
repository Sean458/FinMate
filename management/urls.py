from django.urls import path


from . import views

app_name = 'management'
urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index, name='index'),
    path('users/register', views.register, name='register'),
    path('users/login', views.login_view, name='login'),
    path('users/logout', views.logout_view, name='logout'),
    path('categories/income', views.category_income, name='category_income'),
    path('categories/expense', views.category_expense, name='category_expense'),
    path('addincome', views.addincome, name='addincome'),
    path('addexpense', views.addexpense, name='addexpense'),
    path('transaction', views.transaction, name='transaction'),
    path('export', views.export, name='export'),
    path('report', views.report, name='report'),
    path('summaryreport', views.summaryreport, name='summaryreport'),
    path('invest', views.invest, name='invest'),

]
