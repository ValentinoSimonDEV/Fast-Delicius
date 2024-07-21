from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse , HttpResponseRedirect
from django.views.generic import View , UpdateView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from .forms import CheckOutForm
from Cart.cart import Cart
import mercadopago , json , requests
import logging


class order_checkout(View):
    def get(self , request):
        cart = Cart(request)
        if cart.len() == 0:
            return redirect('index')
        form = CheckOutForm()
        context = {
            'cart' : cart,
            'form' : form,
        }
        return render(request , 'orders/checkout.html' , context)

    def post(self , request):
        cart = Cart(request)
        if request.method == 'POST' and cart.len() > 0:
            form = CheckOutForm(request.POST)
            if form.is_valid():
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                existing_order = Order.objects.filter(session_key=session_key , status='Pending').first()
                if existing_order:
                    return redirect('my_orders')
                order = Order.objects.create(
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                    email = form.cleaned_data['email'],
                    postal_code = form.cleaned_data['postal_code'],
                    city = form.cleaned_data['city'],
                    address = form.cleaned_data['address'],
                    phone = form.cleaned_data['phone']
                )
                total = 0
                for item in cart:
                    total += item['price'] * item['quantity']
                    OrderItem.objects.create(
                        order = order,
                        product = item['product'],
                        price = item['price'],
                        quantity = item['quantity']
                    )
                order.total = total
                order.save()
                cart.clear()
                return redirect('create_preference' , order_id = order.id)
            else:
                form = CheckOutForm()


class my_order(View):
    def get(self , request):
        session_key = request.session.session_key
        if not session_key:
            return render(request , 'orders/my_orders.html' , {'orders' : []})
        orders = Order.objects.filter(session_key=session_key).first()
        context = {
            'orders' : orders
        }
        return render(request , 'orders/my_order.html' , context)


logger = logging.getLogger(__name__)

class create_preference(View):
    def get( self , request , order_id):
        order = get_object_or_404(Order , id = order_id)
        sdk = mercadopago.SDK("APP_USR-6564767660186467-071215-bf95ffce87575b69db4c78b8905e179d-1899373822")
        preference_data = {
            "items": [
                {
                    "title": f"Order #{order.id}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(order.total),
                }
            ],
            "payer": {
                "email": order.email
            },
            "back_urls": {
                "success": request.build_absolute_uri('/success/'),
                "failure": request.build_absolute_uri('/failure/'),
                "pending": request.build_absolute_uri('/pending/'),
            },
            "auto_return": "approved",
            "notification_url": "https://head-jerry-valentinodeveloper-cbfef9c4.koyeb.app/webhook/",
            "external_reference": str(order.id),

        }
        try:
            result = sdk.preference().create(preference_data)
            print("preference created successfully" , result)
            preference = result['response']
            return HttpResponseRedirect(preference['init_point'])
        
        except Exception as e:
            print("Error creating preference:", str(e))
            return JsonResponse({'error' : str(e)} , status=400)
        

@method_decorator(csrf_exempt, name='dispatch')
class Webhook(View):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                notification_data = json.loads(request.body)
                print('Webhook received', notification_data)

                # Verificar la presencia de 'action'
                if 'action' in notification_data:
                    if notification_data['action'] == 'payment.created':
                        payment_id = notification_data.get('data', {}).get('id')
                        if payment_id:
                            order = get_object_or_404(Order, payment_id=payment_id)
                            order.payment_state = True
                            order.save()
                        else:
                            return JsonResponse({'status': 'error', 'message': 'ID de pago no encontrado en la notificación'}, status=400)
                
                # Verificar la presencia de 'topic'
                elif 'topic' in notification_data:
                    if notification_data['topic'] == 'payment':
                        resource_url = notification_data.get('resource')
                        if resource_url:
                            payment_id = resource_url.split('/')[-1]
                            order = get_object_or_404(Order, payment_id=payment_id)
                            order.payment_state = True
                            order.save()
                        else:
                            return JsonResponse({'status': 'error', 'message': 'Resource URL no encontrada en la notificación'}, status=400)
                
                else:
                    return JsonResponse({'status': 'error', 'message': 'Formato de datos no reconocido'}, status=400)
                
                return JsonResponse({'status': 'success'}, status=200)
            
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

class payment_success(View):
    def get(self , request):
        order = Order.objects.filter(session_key = request.session.session_key).first()
        if order:
            order.payment_state = True
            order.save()
        return render(request , 'payments/success.html')

class payment_failure(View):
    def get(self , request):
        order = Order.objects.filter(session_key = request.session.session_key).first()
        if order:
            order.payment_state = False
            order.delete()
        return render(request , 'payments/failure.html')

class payment_pending(View):
    def get(self , request):
        return render(request , 'payments/pending.html')

@method_decorator(login_required, name='dispatch')
class view_orders(View):
    def get(self , request):
        status_filter = request.GET.get('status', 'pending')
        if status_filter == 'pending':
            orders = Order.objects.filter(status='Pending', payment_state=True)
        elif status_filter == 'cancelled':
            orders = Order.objects.filter(status='Cancelled', payment_state=True)
        elif status_filter == 'completed':
            orders = Order.objects.filter(status='Completed', payment_state=True)
        elif status_filter == 'all':
            orders = Order.objects.filter()
        else:
            orders = Order.objects.filter(status='Pending')
        
        context = {
            'orders':orders,
            'status_filter': status_filter
        }
        return render(request , 'orders/list_orders.html' , context)

@method_decorator(login_required, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class update_order_status(View):
    def post(self , request , order_id):
        order = get_object_or_404(Order , id=order_id)
        new_status = request.POST.get('status')
        if new_status in ['Pending' , 'Completed' , 'Cancelled']:
            order.status = new_status
            order.save()
        return redirect('view_orders')
    

class delete_orders(View):
    def post(self , request , order_id):
        if request.method == 'POST':
            order = get_object_or_404(Order , id=order_id)
            order.delete()
            return redirect('view_orders')

