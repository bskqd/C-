from django.db import models


class NovaPoshtaArea(models.Model):
    """
    Справочник областей компании «Новая Почта»
    """
    name_ukr = models.CharField(max_length=100)
    ref = models.CharField(max_length=100)
    areas_center = models.CharField(max_length=100)


class TypeDescription(models.Model):
    """
    Типы населенных пукнтов
    """
    name_ukr = models.CharField(max_length=100)
    ref_description_NP = models.CharField(max_length=100)


class NovaPoshtaCity(models.Model):
    """
    Справочник городов компании «Новая Почта»
    """
    name_ukr = models.CharField(max_length=100)
    ref = models.CharField(max_length=100)
    area = models.ForeignKey(NovaPoshtaArea, on_delete=models.PROTECT)
    id_city = models.IntegerField()
    type_description = models.ForeignKey(TypeDescription, on_delete=models.PROTECT)


class NovaPoshtaWarehouse(models.Model):
    """
    Справочник отделений Новой почты
    """
    number = models.IntegerField()
    code = models.BigIntegerField()
    name_ukr = models.CharField(max_length=255)
    short_address = models.CharField(max_length=255)
    ref = models.CharField(max_length=100)
    city = models.ForeignKey(NovaPoshtaCity, on_delete=models.CASCADE)


class TypeStreet(models.Model):
    """
    Типы частей города (улица, площадь и т.п.)
    """
    name_ukr = models.CharField(max_length=25)


class NovaPoshtaStreet(models.Model):
    """
    Справочник улиц компании «Новая Почта»
    """
    city = models.ForeignKey(NovaPoshtaCity, on_delete=models.CASCADE)
    name_ukr = models.CharField(max_length=100)
    ref = models.CharField(max_length=100)
    type_street = models.ForeignKey(TypeStreet, on_delete=models.PROTECT)

    class Meta:
        unique_together = ['city', 'ref']

    @property
    def get_full_name_ukr(self):
        return self.type_street.name_ukr + ' ' + self.name_ukr


class DeliveryAbstractModel(models.Model):
    is_courier = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15)
    other_street = models.CharField(max_length=200, null=True, blank=True)
    house = models.CharField(max_length=20, null=True, blank=True)
    apartment = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        abstract = True


class NovaPoshtaDelivery(DeliveryAbstractModel):
    """
    Доставка Новая почта
    """
    city = models.ForeignKey(NovaPoshtaCity, on_delete=models.PROTECT, null=True, blank=True)
    street = models.ForeignKey(NovaPoshtaStreet, on_delete=models.PROTECT, null=True, blank=True)
    warehouse = models.ForeignKey(NovaPoshtaWarehouse, on_delete=models.PROTECT, null=True, blank=True)

    @property
    def ukr_name_post(self):
        return 'NovaPoshta'


class UkrPoshtaDelivery(DeliveryAbstractModel):
    """
    Доставка Укр Почтой
    """

    @property
    def ukr_name_post(self):
        return 'UkrPoshta'
