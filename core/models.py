from django.db import models
from common.constants import REQUEST_STATUS_CHOICES, BILLING_STATUS_CHOICES, TABLE_STATUS_CHOICES, \
    PAYMENT_STATUS_CHOICES
from common.enums import PaymentStatus


class Menu(models.Model):
    category_name = models.CharField(max_length=255)
    menu_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    restaurant_id = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    available = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.menu_name

    class Meta:
        verbose_name = "menu"


class WaiterHistory(models.Model):
    restaurant_id = models.CharField(max_length=225)
    order_id = models.CharField(max_length=255)
    waiter_id = models.CharField(max_length=255)
    table_no = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "waiter_history"


class Universal(models.Model):
    id = models.CharField(max_length=255)
    username = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    phone_number = models.BigIntegerField()
    name = models.CharField(max_length=255)
    date_column = models.DateField()
    resId = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "universal"


class Order(models.Model):
    restaurant_id = models.CharField(max_length=255)
    id = models.CharField(max_length=255, primary_key=True)
    table_no = models.CharField(max_length=255)
    food_name = models.CharField(max_length=1000, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_time = models.DateTimeField()
    user_id = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=25)
    status = models.CharField(max_length=25)
    menu_id = models.CharField(max_length=255)
    category_id = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"


class DJ(models.Model):
    thumbnail = models.CharField(max_length=255)
    song_name = models.CharField(max_length=255)
    duration = models.TimeField()
    artist = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    set_waiting_time = models.TimeField()
    request_status = models.CharField(max_length=255, choices=REQUEST_STATUS_CHOICES)
    restaurant_id = models.IntegerField()  # Foreign Key
    id = models.BigIntegerField(primary_key=True)
    manager = models.ForeignKey("Manager", on_delete=models.DO_NOTHING)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.song_name

    class Meta:
        verbose_name = "dj"


class BillingHistory(models.Model):
    restaurant_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    table = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_and_time = models.DateTimeField()
    status = models.CharField(max_length=255, choices=BILLING_STATUS_CHOICES)
    payment_status = models.CharField(max_length=255, choices=PAYMENT_STATUS_CHOICES, default=PaymentStatus.PAID.value)
    waiter_id = models.IntegerField()
    payment_time = models.DateTimeField()
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "billing_history"


class TableNo(models.Model):
    table_no = models.CharField(max_length=255, primary_key=True)
    transaction_id = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    status = models.CharField(max_length=255, choices=TABLE_STATUS_CHOICES)
    restaurant_id = models.IntegerField()  # Foreign Key
    manager = models.ForeignKey("Manager", on_delete=models.CASCADE)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "table_no"


class Item(models.Model):
    restaurant_id = models.CharField(max_length=255)  # Foreign Key
    category_id = models.CharField(max_length=255)  # Foreign Key
    id = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255)
    price = models.BigIntegerField()
    url = models.CharField(max_length=1000)
    description = models.CharField(max_length=255)
    menu_id = models.CharField(max_length=255)
    category_name = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"


class OrderItems(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Tax(models.Model):
    restaurant_id = models.BigIntegerField()
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    GST = models.DecimalField(max_digits=5, decimal_places=2)
    offer = models.DecimalField(max_digits=5, decimal_places=2)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"Restaurant ID: {self.restaurant_id}, Tax: {self.tax}, GST: {self.GST}, Offer: {self.offer}"

    class Meta:
        verbose_name = "tax"
        verbose_name_plural = "taxes"


class Allotment(models.Model):
    user_id = models.CharField(max_length=255)
    restaurant_id = models.CharField(max_length=255)
    table_id = models.CharField(max_length=255)
    reserved_status = models.SmallIntegerField()
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"Allotment - User ID: {self.user_id}, Restaurant ID: {self.restaurant_id}, Table ID: {self.table_id}, Reserved Status: {self.reserved_status}"


class RestaurantTable(models.Model):
    table_no = models.ForeignKey(TableNo, on_delete=models.CASCADE)
    restaurant_id = models.CharField(max_length=255)  # Foreign key
    url = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"Table - Table No: {self.table_no}, Restaurant ID: {self.restaurant_id}, URL: {self.url}"

    class Meta:
        verbose_name = "restaurant_table"
        verbose_name_plural = "restaurant_tables"


class Manager(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    restaurant_id = models.IntegerField()
    access_token = models.SmallIntegerField()
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"User - Username: {self.username}, Password: {self.password}, Restaurant ID: {self.restaurant_id}, Access Token: {self.access_token}"


class RestaurantWaiter(models.Model):
    restaurant_id = models.CharField(max_length=255)
    waiter_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    date = models.DateField()
    phone = models.BigIntegerField()
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"Waiter - Restaurant ID: {self.restaurant_id}, Waiter ID: {self.waiter_id}, Name: {self.name}, Email: {self.email}, Date: {self.date}, Phone: {self.phone}"


class UserOrderHistory(models.Model):
    order_id = models.CharField(max_length=255)
    menu_id = models.CharField(max_length=255)
    quantity = models.IntegerField()
    customer_id = models.CharField(max_length=255)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"OrderItem - Order ID: {self.order_id}, Menu ID: {self.menu_id}, Quantity: {self.quantity}, Customer ID: {self.customer_id}"

    class Meta:
        verbose_name = "user_orders_history"
