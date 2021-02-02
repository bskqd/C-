from directory.models import Commisioner


def get_user_full_name(obj):
    if hasattr(obj, 'userprofile'):
        return f'{obj.last_name} {obj.first_name} {obj.userprofile.middle_name}'
    return f'{obj.last_name} {obj.first_name}'


def forward_func_remove_user(apps, schema_editor):
    CommissionerSignProtocol = apps.get_model('signature', 'CommissionerSignProtocol')
    db_alias = schema_editor.connection.alias
    for sign in CommissionerSignProtocol.objects.using(db_alias).filter(signer__isnull=True):
        signer_full_name = get_user_full_name(sign.user)
        commissioner, _ = Commisioner.objects.using(db_alias).get_or_create(
            name__iexact=signer_full_name,
            defaults={'name': signer_full_name, 'user_id': sign.user_id}
        )
        sign.signer_id = commissioner.pk
        sign.save()
