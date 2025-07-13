from django.db import models
from django.conf import settings
from decimal import Decimal
import stripe
from products.models import Product
from accounts.models import User, GuestUser, Address
from .order_item_model import OrderItem
from django.db.models import Q

stripe.api_key = settings.STRIPE_SECRET_KEY


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    guest = models.ForeignKey(GuestUser, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        name = self.user.email if self.user else f"Guest#{self.guest.guest_id}" if self.guest else "Unknown"
        return f"Order #{self.id} by {name}"

    def mark_paid(self):
        self.paid = True
        self.save()

    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())

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

        order = cls.objects.create(user=user, total_amount=cart.total_price, address=address)

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

        order = cls.objects.create(
            user=user,
            total_amount=product.price_per_piece,
            address=address
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=product.price_per_piece
        )

        product.stock_quantity -= 1
        product.save()
        return order

    @classmethod
    def create_guest_order(cls, guest_data, cart_items, skip_clear=False):
        """
        Creates guest order and linked guest+address.

        guest_data: dict with keys:
        - name, email, phone
        - street_address, city, province, country, zip_code
        - payment_method (optional)
        """
        if not cart_items:
            raise ValueError("Cart is empty.")

        # Create GuestUser
        guest = GuestUser.create_guest(
            name=guest_data.get("name"),
            email=guest_data.get("email"),
            phone=guest_data.get("phone")
        )

        # Create Address
        address = Address.objects.create(
            guest=guest,
            full_name=guest_data.get("name"),
            phone=guest_data.get("phone"),
            street_address=guest_data.get("street_address"),
            zip_code=guest_data.get("zip_code"),
            city=guest_data.get("city"),
            province=guest_data.get("province"),
            country=guest_data.get("country"),
            is_default=False,
        )

        # Create Order
        order = cls.objects.create(
            guest=guest,
            address=address,
            total_amount=Decimal("0.00"),
            payment_method=guest_data.get('payment_method', 'cod')
        )

        total = Decimal("0.00")

        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            unit_price = item['unit_price']

            if quantity > product.stock_quantity:
                raise ValueError(f"Insufficient stock for {product.product_name}")

            subtotal = quantity * unit_price
            total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            product.stock_quantity -= quantity
            product.save()

        order.total_amount = total
        order.save()
        return order

    from django.db.models import Q

    @staticmethod
    def filter_by_criteria(user_email=None, city=None, province=None, country=None, zip_code=None):
        orders = Order.objects.select_related('user', 'guest', 'address').order_by('-order_date')

        if user_email:
            orders = orders.filter(
                Q(user__email__icontains=user_email) |
                Q(guest__email__icontains=user_email)
            )
        if city:
            orders = orders.filter(address__city__icontains=city)
        if province:
            orders = orders.filter(address__province__icontains=province)
        if country:
            orders = orders.filter(address__country__icontains=country)
        if zip_code:
            orders = orders.filter(address__zip_code__icontains=zip_code)

        return orders


    @staticmethod
    def parse_guest_cart_items(session_cart):

        cart_items = []
        total_price = Decimal('0.00')

        for item in session_cart if isinstance(session_cart, list) else session_cart.items():
            pid = item.get('product_id') if isinstance(item, dict) else item[0]
            qty = item.get('quantity') if isinstance(item, dict) else item[1]

            try:
                product = Product.objects.get(pk=pid)
                subtotal = qty * product.price_per_piece
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'subtotal': subtotal,
                    'unit_price': product.price_per_piece,
                })
                total_price += subtotal
            except Product.DoesNotExist:
                continue

        return cart_items, total_price