from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, verbose_name='الوصف'),
        ),
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[('low','منخفضة'),('medium','متوسطة'),('high','عالية'),('urgent','عاجلة')],
                default='medium', max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-created_at'], 'verbose_name': 'مهمة', 'verbose_name_plural': 'المهام'},
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[('todo','لم تبدأ'),('in_progress','جارية'),('done','مكتملة')],
                default='todo', max_length=20,
            ),
        ),
    ]
