from django.urls import path
from tracker.views import home,delete_expense,edit_expense,export_expenses_pdf



urlpatterns = [
    path('',home,name='home'),
    path('delete_expense/<int:id>/',delete_expense,name='delete-expense'),
    path('edit_expense/<int:id>/', edit_expense, name='edit-expense'),
    path('export_expenses_pdf/', export_expenses_pdf, name='export-expenses-pdf'),
]