# import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse

from ..consts import SHOW_POST
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
USER_NAME = 'testuser'
GROUP_NAME = 'Тестовая група'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_NAME_ONE_POST = 'Тестовая група для одного поста'
GROUP_SLUG_ONE_POST = 'test-non-slug'
GROUP_DESCRIPTION_POST = 'Тестовое описание группы для одного поста'
IMAGE_NAME = 'test.gif'
IMAGE_NAME_ONE_POST = 'new_group_images.gif'
POST_TEXT = 'Отсутствующее тестовое описание'
POST_TEXT_ONE_POST = 'Тестовый пост в новой группе'


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title=GROUP_NAME,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_one_post = Group.objects.create(
            title=GROUP_NAME_ONE_POST,
            slug=GROUP_SLUG_ONE_POST,
            description=GROUP_DESCRIPTION_POST,
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
        # for number in range(SHOW_POST + 1):
        #     # image_post = SimpleUploadedFile(
        #     #     name=f'{IMAGE_NAME}_{number}',
        #     #     content=cls.small_gif,
        #     #     content_type='image/gif',
        #     # )
        #     Post.objects.create(
        #         author=cls.user,
        #         text=POST_TEXT,
        #         group=cls.group,
        #         image=image_post,
        #     )
        # cls.post = Post.objects.get(pk=1)
        cls.url_address_map = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ),
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ),
        }
        cls.url_templation_map = {
            cls.url_address_map['index']: 'posts/index.html',
            cls.url_address_map['group_list']: 'posts/group_list.html',
            cls.url_address_map['profile']: 'posts/profile.html',
            cls.url_address_map['post_detail']: 'posts/post_detail.html',
            cls.url_address_map['post_create']: 'posts/create_post.html',
            cls.url_address_map['post_edit']: 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_test(self, first_object, equiv_object):
        post_author = first_object.author.username
        post_group = first_object.group.title
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_author, equiv_object.author.username)
        self.assertEqual(post_group, equiv_object.group.title)
        self.assertEqual(post_text, equiv_object.text)
        self.assertEqual(post_image, equiv_object.image)

    def test_views_correct_templation(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template in self.url_templation_map.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_views_index_correct_content(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['index'])
        first_object = response.context['page_obj'][0]
        self.post_test(first_object, self.post)

    def test_views_group_posts_correct_content(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['group_list']
        )
        first_object = response.context['page_obj'][0]
        group = response.context['group']
        self.post_test(first_object, self.post)
        self.assertEqual(group.title, GROUP_NAME)
        self.assertEqual(group.description, GROUP_DESCRIPTION)

    def test_views_profile_correct_content(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.url_address_map['profile'])
        first_object = response.context['page_obj'][0]
        author = response.context['author']
        self.post_test(first_object, self.post)
        self.assertEqual(author.username, USER_NAME)

    def test_views_post_detail_correct_content(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['post_detail']
        )
        first_object = response.context['post']
        self.post_test(first_object, self.post)

    def test_views_post_create_correct_content(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['post_create']
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_edit_correct_content(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.url_address_map['post_edit']
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        is_edit = response.context['is_edit']
        post_id = response.context['post_id']
        self.assertEqual(is_edit, True)
        self.assertEqual(post_id, 1)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # def test_views_paginator_first_page_correct(self):
    #     """Работа peginstor первой страници"""
    #     for name in list(self.url_address_map.values())[:3]:
    #         with self.subTest(name=name):
    #             response = self.authorized_client.get(name)
    #             self.assertEqual(
    #                 len(response.context['page_obj']), SHOW_POST
    #             )
    #
    # def test_views_paginator_second_page_correct(self):
    #     """Работа peginstor следующей страници"""
    #     for name in list(self.url_address_map.values())[:3]:
    #         with self.subTest(name=name):
    #             response = self.authorized_client.get(name + '?page=2')
    #             self.assertEqual(
    #                 len(response.context['page_obj']),
    #                 1
    #             )

    def test_views_create_post_in_gruop_correct(self):
        """Проверка верного отображения добавленного поста"""
        post_one = Post.objects.create(
            author=self.user,
            text=POST_TEXT_ONE_POST,
            group=self.group_one_post,
            image=self.image_post,
        )
        templation_name_non_group = (
            self.url_address_map['index'],
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_one_post.slug}
            ),
            self.url_address_map['profile'],
        )
        for name in templation_name_non_group:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                first_object = response.context['page_obj'][0]
                self.post_test(first_object, post_one)
        response = self.authorized_client.get(
            self.url_address_map['group_list']
        )
        first_object = response.context['page_obj'][0]
        self.assertNotEqual(first_object.group.title, post_one.group.title)
        self.assertNotEqual(first_object.text, post_one.text)
