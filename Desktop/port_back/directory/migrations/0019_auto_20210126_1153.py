from django.db import migrations


def add_scan_doc(apps, schema_editor):
    TypeDocument = apps.get_model("directory", "TypeDocument")
    db_alias = schema_editor.connection.alias
    TypeDocument.objects.using(db_alias).create(id=750, name='Scan document', is_disable=False, event='Output')


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0018_auto_20210126_0824'),
    ]

    operations = [
        migrations.RunPython(add_scan_doc),
    ]
