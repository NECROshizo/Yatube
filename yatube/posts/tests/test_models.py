from django.test import TestCase

from ..models import Group, Post, User
from ..models import FIRST_CHAR

USER_NAME = 'testuser'
GROUP_NAME = 'Тестовая група'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title=GROUP_NAME,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group
        field_str = {
            post.text[:FIRST_CHAR]: str(post),
            group.title: str(group),
        }
        for correct_object_name, expected_value in field_str.items():
            with self.subTest(correct_object_name=correct_object_name):
                self.assertEqual(correct_object_name, expected_value)

    def test_post_have_correct_help_text(self):
        """Проверяем, что у моделb Post корректно работает help_text."""
        post = self.post
        field_help_text = {
            'text': 'Основной текст поста',
            'pub_date': 'Дата когда был создан пост',
            'group': 'Группа к которой будет относится пост',
            'author': 'Автор данного поста',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_post_have_correct_verbose_name(self):
        """Проверяем, что у моделb Post корректно работает verbose_name."""
        post = self.post
        field_help_text = {
            'text': 'Содержание поста',
            'pub_date': 'Дата публикации',
            'group': 'Група',
            'author': 'Автор',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
