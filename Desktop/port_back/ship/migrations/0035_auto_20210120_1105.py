from django.db import migrations


def delete_func_ios(apps, schema_editor):
    IORequest = apps.get_model("ship", "IORequest")
    Port = apps.get_model("directory", "Port")
    db_alias = schema_editor.connection.alias
    IORequest.objects.using(db_alias).filter(port__is_disable=True).exclude(id=0).delete()
    Port.objects.using(db_alias).filter(is_disable=True).exclude(id=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ship', '0034_iorequest_cifra_uuid'),
    ]

    operations = [
        migrations.RunPython(delete_func_ios),
    ]
