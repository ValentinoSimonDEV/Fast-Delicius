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
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class order_checkout(View):
    @swagger_auto_schema(
        operation_description="Página de checkout para la orden",
        responses={200: openapi.Response('Checkout page', CheckOutForm)}
    )
    def get(self, request):
        cart = Cart(request)
        if cart.len() == 0:
            return redirect('index')
        form = CheckOutForm()
        context = {
            'cart': cart,
            'form': form,
        }
        return render(request, 'orders/checkout.html', context)

    @swagger_auto_schema(
        operation_description="Procesar la orden del checkout",
        request_body=CheckOutForm,
        responses={201: openapi.Response('Order created successfully')}
    )
    def post(self, request):
        cart = Cart(request)
        if request.method == 'POST' and cart.len() > 0:
            form = CheckOutForm(request.POST)
            if form.is_valid():
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                existing_order = Order.objects.filter(session_key=session_key, status='Pending').first()
                if existing_order:
                    return redirect('my_orders')
                order = Order.objects.create(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    postal_code=form.cleaned_data['postal_code'],
                    city=form.cleaned_data['city'],
                    address=form.cleaned_data['address'],
                    phone=form.cleaned_data['phone']
                )
                total = 0
                for item in cart:
                    total += item['price'] * item['quantity']
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                order.total = total
                order.save()
                cart.clear()
                return redirect('create_preference', order_id=order.id)
            else:
                form = CheckOutForm()

class my_order(View):
    @swagger_auto_schema(
        operation_description="Ver las órdenes del usuario",
        responses={200: openapi.Response('User orders')}
    )
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return render(request, 'orders/my_orders.html', {'orders': []})
        orders = Order.objects.filter(session_key=session_key).first()
        context = {
            'orders': orders
        }
        return render(request, 'orders/my_order.html', context)

logger = logging.getLogger(__name__)

class create_preference(View):
    @swagger_auto_schema(
        operation_description="Crear preferencia de pago para la orden",
        responses={200: openapi.Response('Preference created successfully')}
    )
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
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
            preference = result['response']
            
            order.payment_id = preference['id']
            order.save()
            
            return HttpResponseRedirect(preference['init_point'])
        except Exception as e:
            logger.error("Error creating preference:", str(e))
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class webhook(View):
    @swagger_auto_schema(
        operation_description="Webhook para recibir notificaciones de MercadoPago",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='ID de la notificación'),
                'topic': openapi.Schema(type=openapi.TYPE_STRING, description='Tópico de la notificación')
            }
        ),
        responses={200: openapi.Response('Webhook received successfully')}
    )
    def post(self, request, *args, **kwargs):
        try:
            if 'id' in request.GET and 'topic' in request.GET:
                topic = request.GET['topic']
                if topic == 'payment':
                    payment_id = request.GET['id']
                    return self.handle_payment(payment_id)
                elif topic == 'merchant_order':
                    merchant_order_id = request.GET['id']
                    return self.handle_merchant_order(merchant_order_id)
                else:
                    return JsonResponse({'status': 'error', 'message': 'Tópico no reconocido'}, status=400)
            else:
                notification_data = json.loads(request.body)
                topic = notification_data.get('topic')
                if topic == 'payment':
                    return self.handle_payment(notification_data['data']['id'])
                elif topic == 'merchant_order':
                    return self.handle_merchant_order(notification_data['id'])
                else:
                    return JsonResponse({'status': 'error', 'message': 'Tópico no reconocido'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Orden no encontrada'}, status=404)
        except Exception as e:
            logger.error("Error processing webhook: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def handle_payment(self, payment_id):
        try:
            payment_info = self.get_payment_info(payment_id)
            external_reference = payment_info.get('external_reference')
            order = get_object_or_404(Order, id=external_reference)
            order.payment_state = payment_info['status'] == 'approved'
            order.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            logger.error("Error handling payment: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def handle_merchant_order(self, merchant_order_id):
        try:
            order_info = self.get_merchant_order_info(merchant_order_id)
            payment_info = order_info.get('payments', [])[0]  # Obtener el primer pago relacionado
            external_reference = order_info.get('external_reference')
            order = get_object_or_404(Order, id=external_reference)
            order.payment_state = payment_info['status'] == 'approved'
            order.status = 'Completed' if order.payment_state else 'Pending'
            order.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            logger.error("Error handling merchant order: %s", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get_payment_info(self, payment_id):
        sdk = mercadopago.SDK('APP_USR-6564767660186467-071215-bf95ffce87575b69db4c78b8905e179d-1899373822')
        payment_info = sdk.payment().get(payment_id)
        return payment_info['response']

    def get_merchant_order_info(self, merchant_order_id):
        sdk = mercadopago.SDK('APP_USR-6564767660186467-071215-bf95ffce87575b69db4c78b8905e179d-1899373822')
        order_info = sdk.merchant_order().get(merchant_order_id)
        return order_info['response']

    @swagger_auto_schema(
        operation_description="Eliminar órdenes no pagadas",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
    class DeleteUnpaidOrders(View):
        def get(self, request):
            time_limit = datetime.datetime.now() - datetime.timedelta(minutes=30)
            unpaid_orders = Order.objects.filter(payment_state=False, created__lt=time_limit)
            unpaid_orders.delete()
            return JsonResponse({'status': 'success', 'message': 'Unpaid orders deleted'})


@swagger_auto_schema(
        operation_description="Redireccion cuando el pago es correcto",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
class payment_success(View):
    def get(self , request):
        order = Order.objects.filter(session_key = request.session.session_key).first()
        if order:
            order.payment_state = True
            order.save()
        return render(request , 'payments/success.html')

@swagger_auto_schema(
        operation_description="Redireccion cuando el pago es incorrecto",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
class payment_failure(View):
    def get(self , request):
        order = Order.objects.filter(session_key = request.session.session_key).first()
        if order:
            order.payment_state = False
            order.delete()
        return render(request , 'payments/failure.html')

@swagger_auto_schema(
        operation_description="Redireccion cuando el pago esta pendiente",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
class payment_pending(View):
    def get(self , request):
        return render(request , 'payments/pending.html')

@swagger_auto_schema(
        operation_description="Vista de todas las ordenes",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
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
            orders = Order.objects.filter(payment_state=True)
        else:
            orders = Order.objects.filter(status='Pending')
        
        context = {
            'orders':orders,
            'status_filter': status_filter
        }
        return render(request , 'orders/list_orders.html' , context)

@swagger_auto_schema(
        operation_description="Actualiza estado de la orden",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
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
    

@swagger_auto_schema(
        operation_description="Elimina las ordenes",
        responses={200: openapi.Response('Unpaid orders deleted')}
    )
class delete_orders(View):
    def post(self , request , order_id):
        if request.method == 'POST':
            order = get_object_or_404(Order , id=order_id)
            order.delete()
            return redirect('view_orders')

