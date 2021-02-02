from datetime import date, timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import back_office.validators
from back_office.models import PriceIORequest, DeadweightPrice, DeadweightPricePeriod


class PriceIORequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceIORequest
        fields = ('id', 'price', 'type_of_form', 'date_start', 'date_end')
        read_only_fields = ('date_end',)

    def update(self, instance, validated_data):
        if instance.date_end:
            raise ValidationError('cannot update record')
        today = date.today()
        if instance.date_start <= today:
            raise ValidationError('Price used - use create')
        date_end = instance.date_start - timedelta(days=1)
        new_date_end = validated_data['date_start'] - timedelta(days=1)
        try:
            current_price = PriceIORequest.objects.get(date_end=date_end, type_of_form=instance.type_of_form)
            current_price.date_end = new_date_end
            current_price.save(update_fields=['date_end'])
        except PriceIORequest.DoesNotExist:
            pass
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DeadweightPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadweightPrice
        fields = ('from_deadweight', 'to_deadweight', 'price')


class DeadweightPricePeriodSerializer(serializers.ModelSerializer):
    prices = DeadweightPriceSerializer(many=True)

    class Meta:
        model = DeadweightPricePeriod
        fields = ('id', 'date_start', 'date_end', 'prices')
        read_only_fields = ('date_end',)
        validators = [back_office.validators.CheckDedweightList()]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['prices'] = sorted(response['prices'], key=lambda x: x['from_deadweight'])
        return response

    def validate(self, attrs):
        date_start = attrs.get('date_start')
        if date_start and date_start <= date.today():
            raise ValidationError('The start date cannot be less than tomorrow')
        if self.instance and self.instance.date_start <= date.today():
            raise ValidationError('Prices are used')
        return super().validate(attrs)

    def create(self, validated_data):
        if DeadweightPricePeriod.objects.filter(date_end__isnull=True).first().date_start > date.today():
            raise ValidationError('New price exists')
        date_start = validated_data.get('date_start')
        deadweight_price = validated_data.pop('prices', None)
        date_end_current = date_start - timedelta(days=1)
        DeadweightPricePeriod.objects.filter(date_end__isnull=True).update(date_end=date_end_current)
        period_obj = DeadweightPricePeriod.objects.create(**validated_data)
        DeadweightPrice.objects.bulk_create(
            [DeadweightPrice(price_period=period_obj, **price) for price in deadweight_price])
        return period_obj

    def update(self, instance, validated_data):
        date_start = validated_data.get('date_start')
        deadweight_price = validated_data.pop('prices', None)
        if deadweight_price:
            instance.prices.all().delete()
            DeadweightPrice.objects.bulk_create(
                [DeadweightPrice(price_period=instance, **price) for price in deadweight_price])
        if date_start:
            current_date_end = instance.date_start - timedelta(days=1)
            new_date_end = date_start - timedelta(days=1)
            DeadweightPricePeriod.objects.filter(date_end=current_date_end).update(date_end=new_date_end)
        super(DeadweightPricePeriodSerializer, self).update(instance, validated_data)
        return instance
