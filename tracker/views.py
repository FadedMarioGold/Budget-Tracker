from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm
from collections import defaultdict
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
# Create your views here.

@login_required
def home(request):
    expenses = Expense.objects.filter(user=request.user) 
    form=ExpenseForm()
    if(request.method=='POST'):
        form=ExpenseForm(request.POST)
        if  form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            
            return redirect('home')
    
    expense_data = defaultdict(float)
    for expense in expenses:
        expense_data[expense.category] += float(expense.amount)

    
    categories = list(expense_data.keys())
    amounts = list(expense_data.values())

    return render(request, "tracker/home.html", {
        "expenses": expenses,
        "categories": json.dumps(categories),
        "amounts": json.dumps(amounts),
        "form":form
        
    })
    

@login_required
def delete_expense(request,id):
    expense=Expense.objects.get(id=id)
    expense.delete()
    messages.success(request, "Item deleted successfully.")
    return redirect('home')
@login_required
def edit_expense(request,id):
    expense=get_object_or_404(Expense, id=id)

    if(request.method=='POST'):
        form=ExpenseForm(request.POST,instance=expense)
        if  form.is_valid():
            form.save()
            return redirect('home')
    else:
        form=ExpenseForm(instance=expense)
    return render(request,'tracker/edit_expense.html',{'form':form})



@login_required
def export_expenses_pdf(request):
    # Fetch all the expenses for the logged-in user
    expenses = Expense.objects.filter(user=request.user)

    # Create a BytesIO object to hold the PDF in memory
    buffer = BytesIO()

    # Create a canvas object for PDF generation
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add a title to the PDF
    p.setFont("Helvetica", 16)
    p.drawString(200, height - 50, "Expense Report")

    # Add table headers
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 100, "Title")
    p.drawString(150, height - 100, "Amount")
    p.drawString(250, height - 100, "Category")
    p.drawString(350, height - 100, "Date")

    # Write each expense as a row in the PDF
    y_position = height - 120
    for expense in expenses:
        p.drawString(50, y_position, expense.title)
        p.drawString(150, y_position, f"Rs. {expense.amount}")
        p.drawString(250, y_position, expense.category)
        p.drawString(350, y_position, expense.date.strftime('%Y-%m-%d'))

        y_position -= 20  # Move down for the next row

    # Save the PDF to the buffer
    p.showPage()
    p.save()

    # Get the PDF data from the buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Return the PDF as an HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses_report.pdf"'
    return response