from django.db import models


class PlacesToSell(models.Model):
    place_name = models.CharField(max_length=64)
    address = models.CharField(max_length=128)
    ip_inn = models.CharField(max_length=32)
    kkt_number = models.CharField(max_length=32)
    fn_number = models.CharField(max_length=32)
    quickresto_kkm_id = models.IntegerField(null=True, blank=True, unique=True)
    quickresto_place_id = models.IntegerField(null=True, blank=True, unique=True)
    quickresto_cookplace_id = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f'{self.place_name}'


class EmployeesList(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64, blank=True, null=True)
    rate_per_hour = models.IntegerField(default=100, null=True)
    quickresto_id = models.IntegerField(blank=True, null=True, unique=True)
    mask_ident = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class PlacePriceModificator(models.Model):
    place_to_sale = models.ForeignKey(PlacesToSell, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'{self.place_to_sale}, {self.price}'


class GoodsBase(models.Model):
    group_name = models.CharField(max_length=64)
    under_group_name = models.CharField(max_length=64)
    dish_name = models.CharField(max_length=64)
    base_price = models.ManyToManyField(PlacePriceModificator, blank=True)
    quickresto_id = models.IntegerField(blank=True, null=True, unique=True)
    keyword_ident = models.CharField(max_length=64, null=True, blank=True, unique=True)

    def __str__(self):
        return f'{self.under_group_name}-{self.dish_name}'


class GoodsToSale(models.Model):
    goods_object = models.ForeignKey(GoodsBase, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.goods_object.dish_name} * {self.amount}'


class SalesData(models.Model):
    shift_number = models.IntegerField(null=True)
    receipt_num = models.IntegerField(null=True)

    receipt_num_inshift = models.IntegerField(null=True)
    deal_date = models.DateTimeField()
    kkt_rnm = models.CharField(max_length=32)
    fnnum = models.CharField(max_length=32)
    address = models.ForeignKey(PlacesToSell, on_delete=models.CASCADE)
    receipt_type = models.CharField(max_length=128,
                                    choices=(
                                        ('sale', 'Продажа'),
                                        ('open_shift', 'Открытие смены'),
                                        ('close_shift', 'Закрытие смены'),
                                    ))
    is_fulled = models.BooleanField(default=False)
    is_uploaded_quickresto = models.BooleanField(default=False)
    sold_goods = models.ManyToManyField(GoodsToSale, blank=True)
    staff_name = models.ForeignKey(EmployeesList, on_delete=models.CASCADE, blank=True, null=True)
    payment_type = models.CharField(max_length=64, blank=True, null=True,
                                    choices=(
                                        ('cash', 'Наличный'),
                                        ('electronic', 'Безналичный'),
                                    ))
    receipt_sum = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    quickresto_shift_id = models.IntegerField(null=True, blank=True, unique=True)
    quickresto_receipt_id = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f'{self.kkt_rnm}, {self.receipt_num}, {self.deal_date}'
