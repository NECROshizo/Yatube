# Generated by Django 2.2.9 on 2022-11-16 09:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0009_auto_20221114_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Картинка'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Текст коментария', verbose_name='Коментарий')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата когда был создан пост', verbose_name='Дата публикации')),
                ('author', models.ForeignKey(help_text='Автор данного поста', on_delete=django.db.models.deletion.CASCADE, related_name='comment', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='posts.Post', verbose_name='Коментируемый пост')),
            ],
        ),
    ]
