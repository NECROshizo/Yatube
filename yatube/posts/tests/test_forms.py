from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

USER_NAME = 'testuser'
USER_NAME_TWO = 'testuser2'
GROUP_NAME = 'Тестовая група'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
IMAGE_NAME = 'test.gif'
POST_TEXT = 'Тестовый пост'
POST_FORM_TEXT = 'Тест текс'
POST_NEW_FORM_TEXT = 'Новый текст'


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.user_two = User.objects.create_user(username=USER_NAME_TWO)
        cls.group = Group.objects.create(
            title=GROUP_NAME,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image_post = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            image=cls.image_post,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_two.force_login(self.user_two)

    def test_create_post_authorized_client_correct(self):
        """Авторизированный пользователей создает пост"""
        posts_count = Post.objects.count()
        form_post = {
            'text': POST_FORM_TEXT,
            'group': self.group.pk,
            'image': self.image_post,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_post,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        redirect = reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        self.assertRedirects(response, (redirect))

    def test_create_post_anonymous_client_correct(self):
        """Гостевой пользователей создает пост"""
        posts_count = Post.objects.count()
        form_post = {
            'text': POST_FORM_TEXT,
            'group': self.group.pk,
            'image': self.image_post,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_post,
            follow=True,
        )
        redirect = '/auth/login/?next=/create/'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, redirect)

    def test_edit_post_authorized_client_correct(self):
        """Авторизированный пользователей корректирует свой пост"""
        posts_count = Post.objects.count()
        form_post = {
            'text': POST_NEW_FORM_TEXT,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_post,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(text=POST_NEW_FORM_TEXT).pk,
            self.post.pk
        )
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        self.assertRedirects(response, (redirect))

    def test_edit_post_anonymous_client_correct(self):
        """Гостевой пользователей корректирует пост"""
        posts_count = Post.objects.count()
        form_post = {
            'text': POST_NEW_FORM_TEXT,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_post,
            follow=True,
        )
        redirect = f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=POST_NEW_FORM_TEXT).exists())
        self.assertRedirects(response, (redirect))

    def test_edit_post_authorized_client_correct(self):
        """Авторизированный пользователей корректирует не свой пост"""
        posts_count = Post.objects.count()
        form_post = {
            'text': POST_NEW_FORM_TEXT,
        }
        response = self.authorized_client_two.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_post,
            follow=True,
        )
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=POST_NEW_FORM_TEXT).exists())
        self.assertRedirects(response, (redirect))
