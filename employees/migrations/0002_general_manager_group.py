from django.db import migrations


def create_general_manager_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='المدير العام')
    group.permissions.set(Permission.objects.all())


def remove_general_manager_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='المدير العام').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_general_manager_group, remove_general_manager_group),
    ]
