from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, ProductCategory, Order, OrderItem
from django.http import HttpResponse
from decimal import Decimal
from django.conf import settings
import stripe
import uuid

def product_list(request):
    products = Product.objects.filter(is_available=True)
    categories = ProductCategory.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug)
        # Add debugging information
        print(f"Found product: {product.name}, Category: {product.category.name}")
        context = {
            'product': product,
            'categories': ProductCategory.objects.all()  # Add categories for navigation
        }
        return render(request, 'store/product_detail.html', context)
    except Exception as e:
        # Return error details for debugging
        return HttpResponse(f"Error: {str(e)}", status=500)

def category_products(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    categories = ProductCategory.objects.all()
    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

@login_required
def cart_detail(request):
    # Initialize cart in session if it doesn't exist
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')

    # Get cart items with product details
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total = product.price * Decimal(str(quantity))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': total
            })
            cart_total += total
        except Product.DoesNotExist:
            # Remove invalid products from cart
            del cart[product_id]
            request.session.modified = True

    return render(request, 'store/cart_detail.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is available
    if not product.is_available or product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is currently out of stock.')
        return redirect('store:product_list')
    
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    
    # Get quantity from POST data or default to 1
    quantity = int(request.POST.get('quantity', 1))
    
    # Calculate total requested quantity (current cart + new request)
    current_cart_quantity = cart.get(product_id, 0)
    total_requested = current_cart_quantity + quantity
    
    # Validate against available stock
    if total_requested > product.stock:
        messages.error(request, f'Sorry, only {product.stock} units of {product.name} are available.')
        return redirect('store:cart_detail')
    
    # Update quantity if product already in cart
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    # Save cart back to session
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart.')
    return redirect('store:cart_detail')

@login_required
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, 'Product removed from cart.')
    
    return redirect('store:cart_detail')

@login_required
def cart_update(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id = str(product_id)
        
        try:
            product = get_object_or_404(Product, id=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            # Validate stock availability
            if quantity > product.stock:
                messages.error(request, f'Sorry, only {product.stock} units of {product.name} are available.')
                return redirect('store:cart_detail')
            
            if quantity > 0:
                cart[product_id] = quantity
                request.session['cart'] = cart
                messages.success(request, 'Cart updated successfully.')
            else:
                del cart[product_id]
                request.session['cart'] = cart
                messages.success(request, 'Product removed from cart.')
        except ValueError:
            messages.error(request, 'Invalid quantity specified.')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
    
    return redirect('store:cart_detail')

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'store/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, 'store/order_detail.html', {
        'order': order
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')

    # Get cart items with product details
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total = product.price * Decimal(str(quantity))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': total
            })
            cart_total += total
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(cart_total * 100),  # Convert to cents
                currency=settings.STRIPE_CURRENCY,
                payment_method_types=['card'],
                metadata={
                    'user_id': request.user.id,
                    'cart_items': str(cart)
                }
            )

            # Create order
            order = Order.objects.create(
                customer=request.user,
                order_number=str(uuid.uuid4().hex[:10]),
                total_amount=cart_total,
                shipping_address=request.POST.get('address'),
                phone_number=request.POST.get('phone', ''),
                status='pending'
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

            # Clear the cart
            request.session['cart'] = {}
            
            messages.success(request, 'Order placed successfully!')
            return redirect('store:order_detail', order_number=order.order_number)

        except stripe.error.CardError as e:
            messages.error(request, f"Payment failed: {e.error.message}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'store/checkout.html', context)

@login_required
def place_order_from_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty.')
            return redirect('store:cart_detail')

        # Get form data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Validate required fields
        if not all([full_name, phone, address]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('store:cart_detail')

        cart_items = []
        cart_total = Decimal('0.00')
        stock_error = False

        # Calculate total and validate products
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                
                # Check stock availability
                if quantity > product.stock:
                    messages.error(request, f'Sorry, only {product.stock} units of {product.name} are available.')
                    stock_error = True
                    continue
                
                total = product.price * Decimal(str(quantity))
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': total
                })
                cart_total += total
            except Product.DoesNotExist:
                continue

        if stock_error:
            return redirect('store:cart_detail')

        # Create order
        order = Order.objects.create(
            customer=request.user,
            order_number=str(uuid.uuid4().hex[:10]),
            total_amount=cart_total,
            shipping_address=f"{full_name}\n{address}",
            phone_number=phone,
            status='processing'
        )

        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
            
            # Update product stock
            product = item['product']
            product.stock -= item['quantity']
            product.save()

        # Clear the cart
        request.session['cart'] = {}
        messages.success(request, 'Order placed successfully!')
        return redirect('store:order_detail', order_number=order.order_number)

    return redirect('store:cart_detail')
