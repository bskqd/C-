from django.db import IntegrityError
from django.db.models import ForeignKey

import sailor.document.models
import sailor.models
import sailor.statement.models
from inspection import models as inspection_models
from itcs import celery_app


@celery_app.task(serializer='pickle')
def sync_document(document_obj):
    model_converted = {
        sailor.document.models.ProtocolSQC: inspection_models.InspProtocolDKK,
        sailor.statement.models.StatementSQC: inspection_models.InspSailorStatementDKK,
        sailor.document.models.QualificationDocument: inspection_models.InspQualificationDocument,
        sailor.models.SailorPassport: inspection_models.InspSailorPassport,
        sailor.document.models.ServiceRecord: inspection_models.InspServiceRecordSailor,
        sailor.statement.models.StatementQualification: inspection_models.InspStatementQualificationDocument,
        sailor.document.models.ProofOfWorkDiploma: inspection_models.InspQualificationDocument,
        sailor.models.Profile: inspection_models.InspProfile
    }
    if not document_obj:
        return False
    save_model = model_converted[document_obj._meta.model]
    data = {}
    if isinstance(document_obj, sailor.document.models.QualificationDocument):
        sync_document(document_obj=document_obj.statement)
    elif isinstance(document_obj, sailor.document.models.ProtocolSQC):
        sync_document(document_obj=document_obj.statement_dkk)
    for field in save_model._meta.fields:
        field_name = field.name
        try:
            if field_name == 'author':
                data[field_name] = document_obj.author.get_full_name()
            elif field_name == 'country':
                data[field_name] = document_obj.country.value
            elif field_name == 'sex':
                data[field_name] = document_obj.sex_id
            elif isinstance(field, ForeignKey):
                field_name_pk = f'{field.name}_id'
                data[field_name_pk] = (getattr(document_obj, field_name)).pk
            else:
                data[field_name] = getattr(document_obj, field_name)
        except AttributeError:
            pass
    if document_obj._meta.model_name == 'proofofworkdiploma':
        data.update({'rank_id': document_obj.diploma.rank_id, 'list_positions': document_obj.diploma.list_positions,
                     'type_document_id': 16})
    try:
        save_model.objects.update_or_create(pk=data['id'], defaults=data)
    except IntegrityError:
        if isinstance(document_obj, sailor.document.models.QualificationDocument):
            sync_document.apply_async(args=(document_obj.statement,))
        elif isinstance(document_obj, sailor.document.models.ProtocolSQC):
            sync_document.apply_async(args=(document_obj.statement_dkk,))


@celery_app.task(serializer='pickle')
def delete_document(instance):
    model_converted = {
        sailor.document.models.ProtocolSQC: inspection_models.InspProtocolDKK,
        sailor.statement.models.StatementSQC: inspection_models.InspSailorStatementDKK,
        sailor.document.models.QualificationDocument: inspection_models.InspQualificationDocument,
        sailor.models.SailorPassport: inspection_models.InspSailorPassport,
        sailor.document.models.ServiceRecord: inspection_models.InspServiceRecordSailor,
        sailor.statement.models.StatementQualification: inspection_models.InspStatementQualificationDocument,
        sailor.document.models.ProofOfWorkDiploma: inspection_models.InspQualificationDocument
    }
    to_delete_model = model_converted[instance._meta.model]
    to_delete_model.objects.filter(id=instance.pk).delete()
