from django.shortcuts import render, redirect, get_object_or_404
from .models import Receipt
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required(login_url='/login/')
def receipts(request):
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')

        try:
            total = float(price) * int(quantity)
            Receipt.objects.create(
                name=name,
                price=price,
                quantity=quantity,
                total=total
            )
            messages.success(request, "Receipt added successfully!")
        except ValueError:
            messages.error(request, "Invalid price or quantity!")

        return redirect('receipts')

    queryset = Receipt.objects.all()

    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    # Calculate the total sum
    total_sum = sum(receipt.total for receipt in queryset)
    context = {'receipts': queryset, 'total_sum': total_sum}
    return render(request, 'receipt.html', context)


@login_required(login_url='/login/')
def update_receipt(request, id):
    receipt = get_object_or_404(Receipt, id=id)

    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')

        try:
            total = float(price) * int(quantity)
            receipt.name = name
            receipt.price = price
            receipt.quantity = quantity
            receipt.total = total
            receipt.save()
            messages.success(request, "Receipt updated successfully!")
        except ValueError:
            messages.error(request, "Invalid price or quantity!")

        return redirect('receipts')

    context = {'receipt': receipt}
    return render(request, 'update_receipt.html', context)


@login_required(login_url='/login/')
def delete_receipt(request, id):
    receipt = get_object_or_404(Receipt, id=id)
    receipt.delete()
    messages.success(request, "Receipt deleted successfully!")
    return redirect('receipts')


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username).first()
        if not user_obj:
            messages.error(request, "Username not found")
            return redirect('login')

        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect('receipts')

        messages.error(request, "Invalid username or password")
        return redirect('login')

    return render(request, "login.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return redirect('register')

        user_obj = User.objects.create(username=username)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, "register.html")


def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


@login_required(login_url='/login/')
def pdf(request):
    queryset = Receipt.objects.all()

    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    # Calculate the total sum
    total_sum = sum(receipt.total for receipt in queryset)

    context = {'receipts': queryset, 'total_sum': total_sum}
    return render(request, 'pdf.html', context)
