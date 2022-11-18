from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
FIRST_CHAR = 15


class Group(models.Model):
    title = models.CharField(
        'Название',
        max_length=200,
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField(
        'Описание группы',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Содержание поста',
        help_text='Основной текст поста',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
        help_text='Дата когда был создан пост',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Група',
        help_text='Группа к которой будет относится пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор данного поста',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:FIRST_CHAR]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
        # blank=True,
        verbose_name='Коментируемый пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор',
        help_text='Автор данного поста',
    )
    text = models.TextField(
        'Коментарий',
        help_text='Текст коментария',
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата когда был создан пост',
    )

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Он вас читает',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор постов',
    )
