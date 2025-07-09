from django.db import models
from django.conf import settings
from products.models import Product
from accounts.models import User
from .order_item_model import OrderItem
from decimal import Decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.user.email if self.user else 'Guest'}"

    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def mark_paid(self):
        self.paid = True
        self.save()

    def create_stripe_session(self, success_url, cancel_url):
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.product_name,
                    },
                    'unit_amount': int(item.unit_price * 100),
                },
                'quantity': item.quantity,
            }
            for item in self.items.all()
        ]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'order_id': str(self.id)},
        )

        self.stripe_session_id = session.id
        self.stripe_payment_intent = session.payment_intent
        self.payment_method = 'stripe'
        self.save()
        return session

    @classmethod
    def create_from_cart(cls, user, cart, address):
        if not cart or not cart.items.exists():
            raise ValueError("Cart is empty or invalid.")

        order = cls.objects.create(user=user, total_amount=cart.total_price)

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in cart.items.all()
        ])

        cart.items.all().delete()
        cart.total_price = Decimal('0.00')
        cart.save()

        return order

    @classmethod
    def create_buy_now(cls, user, product, address):
        if product.stock_quantity < 1:
            raise ValueError("Product is out of stock.")

        order = cls.objects.create(user=user, total_amount=product.price_per_piece)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=product.price_per_piece
        )
        return order

    @classmethod
    def create_guest_order(cls, guest_data, cart_items, skip_clear=False):
        if not cart_items:
            raise ValueError("Cart is empty.")

        total = sum(item['quantity'] * item['unit_price'] for item in cart_items)

        order = cls.objects.create(
            user=None,
            total_amount=total,
            payment_method=guest_data.get('payment_method', 'cod')
        )

        for item in cart_items:
            if item['quantity'] > item['product'].stock_quantity:
                raise ValueError(f"Insufficient stock for {item['product'].product_name}")

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )

            item['product'].stock_quantity -= item['quantity']
            item['product'].save()

        return order

    @staticmethod
    def filter_by_criteria(user_email=None, city=None, province=None, country=None, zip_code=None):
        orders = Order.objects.select_related('user').order_by('-order_date')
        if user_email:
            orders = orders.filter(user__email__icontains=user_email)
        return orders
