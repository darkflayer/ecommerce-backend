from .models import Product,Order
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
import razorpay,json
from django.views.decorators.csrf import csrf_exempt

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

# Order List
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'products/order_list.html', {'orders': orders})

# Create Order
def create_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        quantity = request.POST.get('quantity')
        address = request.POST.get('address')

        product = get_object_or_404(Product, id=product_id)
        Order.objects.create(
            product=product,
            customer_name=customer_name,
            customer_email=customer_email,
            quantity=quantity,
            address=address
        )
        return redirect('order_list')

    products = Product.objects.all()
    return render(request, 'products/create_order.html', {'products': products})

# Order Detail
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'products/order_detail.html', {'order': order})

# Update Order
def update_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.order_status = request.POST.get('order_status')
        order.save()
        return redirect('order_list')

    return render(request, 'products/update_order.html', {'order': order})

# Delete Order
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')

    return render(request, 'products/delete_order.html', {'order': order})



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Create Razorpay Order
    payment_data = {
        "amount": int(order.product.price * order.quantity * 100),  # Amount in paise
        "currency": "INR",
        "receipt": f"order_{order_id}",
        "payment_capture": 1  # Auto-capture payment
    }

    razorpay_order = razorpay_client.order.create(data=payment_data)
    order.razorpay_order_id = razorpay_order['id']  # Save Razorpay order ID in DB
    order.save()

    context = {
        "order": order,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "callback_url": f"https://ecommerce-backend-32vy.onrender.com/products/payment/success/"
    }

    return render(request, 'products/payment_page.html', context)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            # Try to extract data from POST first (Form-Encoded)
            data = request.POST

            # If POST data is empty, fall back to JSON data extraction
            if not data:
                data = json.loads(request.body)

            # Verify Signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature'),
            })

            # Check if the order exists
            try:
                order = Order.objects.get(razorpay_order_id=data.get('razorpay_order_id'))
                order.razorpay_payment_id = data.get('razorpay_payment_id')
                order.razorpay_signature = data.get('razorpay_signature')
                order.order_status = 'Paid'
                order.save()

                return render(request, 'products/payment_success.html', {"order": order})

            except Order.DoesNotExist:
                return render(request, 'products/payment_failed.html', {
                    "error": "Order not found in the database."
                })

        except json.JSONDecodeError:
            return render(request, 'products/payment_failed.html', {
                "error": "Invalid JSON data received. Ensure webhook data is correctly formatted."
            })

        except razorpay.errors.SignatureVerificationError:
            return render(request, 'products/payment_failed.html', {
                "error": "Signature verification failed. Payment may be tampered with."
            })

        except Exception as e:
            return render(request, 'products/payment_failed.html', {
                "error": str(e)
            })

    return render(request, 'products/payment_failed.html', {
        "error": "Invalid request method."
    })
