from django.db import models

from core.models import DateTimesABC, AuthorABC


class NameABCModel(models.Model):
    name = models.CharField(max_length=255, default='')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class IsDisableABCModel(models.Model):
    is_disable = models.BooleanField(default=False)

    class Meta:
        abstract = True


class TypeVessel(NameABCModel, IsDisableABCModel):
    pass


class Flag(NameABCModel, IsDisableABCModel):
    image = models.FileField(upload_to='flags/', null=True)


class StaffPosition(NameABCModel, IsDisableABCModel):
    pass


def towing_company_docs_upload_path(instance, filename):
    return f'towing_company_doc/{instance.author.username}/{filename}'


def tow_docs_upload_path(instance, filename):
    return f'tow_doc/{instance.author.username}/{filename}'


class Port(NameABCModel, IsDisableABCModel):
    position_capitan_ukr = models.CharField(max_length=255, default='', blank=True)
    position_capitan_eng = models.CharField(max_length=255, default='', blank=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(null=True, blank=True)
    harbor_master = models.ForeignKey('core.HarborMaster', on_delete=models.SET_NULL, related_name='ports', null=True)


class StatusDocument(IsDisableABCModel, NameABCModel):
    color = models.CharField(max_length=10, default='', blank=True)
    description = models.CharField(max_length=255, default='', blank=True)
    service = models.CharField(max_length=50, default='', blank=True)


class GroupTypeDocumnet(NameABCModel):
    """
    Groups of document types
    """
    pass


class TypeDocument(NameABCModel, IsDisableABCModel):
    """
    Types of documents required to input/output the port
    """
    INPUT = 'Input'
    OUTPUT = 'Output'
    IN_OUT = 'Input/Output'
    TYPE_CHOICES = (
        (INPUT, INPUT),
        (OUTPUT, OUTPUT),
        (IN_OUT, IN_OUT),
    )
    event = models.CharField(max_length=20, choices=TYPE_CHOICES, default=IN_OUT)
    group = models.ForeignKey(GroupTypeDocumnet, on_delete=models.PROTECT, null=True, blank=True)


class Contacts(IsDisableABCModel):
    PHONE = 'phone'
    VIBER = 'viber'
    TELEGRAM = 'telegram'
    EMAIL = 'email'
    TYPE_CONTACTS_CHOICES = (
        (PHONE, PHONE),
        (VIBER, VIBER),
        (TELEGRAM, TELEGRAM),
        (EMAIL, EMAIL),
    )
    value = models.CharField(max_length=20)
    type_contact = models.CharField(max_length=20, choices=TYPE_CONTACTS_CHOICES, default=PHONE)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='contacts')


class Agency(DateTimesABC, AuthorABC, IsDisableABCModel):
    short_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    post_address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    IBAN = models.CharField(max_length=50, null=True, blank=True)
    MFO = models.CharField(max_length=50, null=True, blank=True)
    EDRPOU = models.CharField(max_length=50, null=True, blank=True)


class TowingCompany(DateTimesABC, AuthorABC, IsDisableABCModel):
    short_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, default='')
    post_address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=255, default='')
    IBAN = models.CharField(max_length=50, default='')
    MFO = models.CharField(max_length=50, default='')
    EDRPOU = models.CharField(max_length=50, default='')
    status = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)


class Tow(DateTimesABC, AuthorABC, IsDisableABCModel):
    IMO = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255, default='')
    power = models.CharField(max_length=255)
    port = models.ForeignKey(Port, null=True, on_delete=models.SET_NULL, related_name='tows')
    status = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)
    busy_to = models.DateTimeField(null=True)


class TowingCompanyDocs(NameABCModel):
    towing_company = models.ForeignKey(TowingCompany, null=True, on_delete=models.CASCADE,
                                       related_name='towing_company_docs')
    file = models.FileField(upload_to=towing_company_docs_upload_path)


class TowDocs(NameABCModel):
    towing_company = models.ForeignKey(Tow, null=True, on_delete=models.CASCADE, related_name='tow_docs')
    file = models.FileField(upload_to=tow_docs_upload_path)


class Country(NameABCModel):
    name_abbr = models.CharField(max_length=10)


class Sex(NameABCModel):
    pass
