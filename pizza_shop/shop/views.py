from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Pizza, Order


# 🏠 Home Page
def index(request):
    return render(request, "shop/index.html", {
        "background_image": "images/home-bg.jpg"
    })


# 🍕 Menu Page
def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, "shop/menu.html", {
        "pizzas": pizzas,
        "background_image": "images/menu-bg.jpg"
    })


# 📦 Order Pizza
def order_pizza(request, pizza_id):
    pizza = Pizza.objects.get(id=pizza_id)

    if request.method == 'POST':
        size = request.POST['size']
        quantity = int(request.POST['quantity'])
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']

        # ✅ Price calculation
        if size == "Small":
            price = pizza.small_price
        elif size == "Medium":
            price = pizza.medium_price
        else:
            price = pizza.large_price

        total = price * quantity

        # ✅ Save Order
        Order.objects.create(
            pizza=pizza,
            size=size,
            quantity=quantity,
            customer_name=name,
            phone=phone,
            address=address,
            total_price=total
        )

        # 📧 Send Email
        message = f"""
New Order Received 🍕
Customer Name: {name}
Phone: {phone}
Address: {address}

Pizza: {pizza.name}
Size: {size}
Quantity: {quantity}
Total Price: ₹{total}
"""

        send_mail(
            subject="New Pizza Order 🍕",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        return redirect('menu')

    return render(request, 'shop/order.html', {'pizza': pizza})


# 📞 Contact Page
def contact(request):
    return render(request, "shop/contact.html", {
        "background_image": "images/contact-bg.jpg"
    })


# 🛒 ADD TO CART
def add_to_cart(request, pizza_id):
    if request.method == "POST":
        size = request.POST.get("size")
        quantity = int(request.POST.get("quantity"))

        cart = request.session.get('cart', {})

        key = f"{pizza_id}_{size}"   # unique key for size

        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            pizza = Pizza.objects.get(id=pizza_id)

            if size == "Small":
                price = pizza.small_price
            elif size == "Medium":
                price = pizza.medium_price
            else:
                price = pizza.large_price

            cart[key] = {
                'pizza_id': pizza_id,
                'name': pizza.name,
                'size': size,
                'price': price,
                'quantity': quantity
            }

        request.session['cart'] = cart

    return redirect('menu')

# 🛒 CART VIEW
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for key, item in cart.items():
        item_total = item['price'] * item['quantity']
        total += item_total

        items.append({
            'key': key,
            'name': item['name'],
            'size': item['size'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })

    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total
    })

def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('menu')

    items = []
    total = 0

    # cart items calculate
    for key, item in cart.items():
        item_total = item['price'] * item['quantity']
        total += item_total

        items.append({
            'key': key,
            'pizza_id': item['pizza_id'],
            'name': item['name'],
            'size': item['size'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })

    if request.method == "POST":
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']

        # store customer details in session (for success page)
        request.session['customer_name'] = name
        request.session['customer_phone'] = phone
        request.session['customer_address'] = address
        request.session['grand_total'] = total
        request.session['order_items'] = items

        # save orders in DB
        for item in items:
            pizza = Pizza.objects.get(id=item['pizza_id'])

            Order.objects.create(
                pizza=pizza,
                size=item['size'],
                quantity=item['quantity'],
                customer_name=name,
                phone=phone,
                address=address,
                total_price=item['total']
            )

        # Email send
        message = f"Customer: {name}\nPhone: {phone}\nAddress: {address}\n\nOrders:\n"

        for item in items:
            message += f"{item['name']} ({item['size']}) x {item['quantity']} = ₹{item['total']}\n"

        message += f"\nGrand Total: ₹{total}"

        send_mail(
            subject="New Cart Order 🍕",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        # clear cart
        request.session['cart'] = {}

        # go to payment
        request.session['order_done'] = True
        return redirect('payment')

    return render(request, 'shop/checkout.html', {
        'items': items,
        'total': total
    })

def remove_from_cart(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]

    request.session['cart'] = cart
    return redirect('cart')

def update_cart(request, key, action):
    cart = request.session.get('cart', {})

    if key in cart:
        if action == "increase":
            cart[key]['quantity'] += 1

        elif action == "decrease":
            cart[key]['quantity'] -= 1

            if cart[key]['quantity'] <= 0:
                del cart[key]

    request.session['cart'] = cart
    return redirect('cart')

def payment(request):
    if not request.session.get('order_done'):
        return redirect('menu')

    if request.method == "POST":
        request.session['order_done'] = False
        return redirect('success')   # ✅ redirect here

    return render(request, 'shop/payment.html')

def order_success(request):
    name = request.session.get('customer_name')
    phone = request.session.get('customer_phone')
    address = request.session.get('customer_address')
    total = request.session.get('grand_total')
    items = request.session.get('order_items', [])

    return render(request, 'shop/success.html', {
        'name': name,
        'phone': phone,
        'address': address,
        'total': total,
        'items': items
    })

from django.http import HttpResponse
from reportlab.pdfgen import canvas


def download_invoice(request):
    name = request.session.get('customer_name', 'Customer')
    phone = request.session.get('customer_phone', '')
    address = request.session.get('customer_address', '')
    total = request.session.get('grand_total', 0)
    items = request.session.get('order_items', [])

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 14)

    p.drawString(200, 800, "Pizza Shop Invoice 🍕")
    p.drawString(50, 770, f"Customer: {name}")
    p.drawString(50, 750, f"Phone: {phone}")
    p.drawString(50, 730, f"Address: {address}")

    y = 690
    p.drawString(50, y, "Items:")
    y -= 30

    for item in items:
        line = f"{item['name']} ({item['size']}) x {item['quantity']} = ₹{item['total']}"
        p.drawString(50, y, line)
        y -= 20

    y -= 20
    p.drawString(50, y, f"Grand Total: ₹{total}")

    p.showPage()
    p.save()

    return response