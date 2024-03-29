import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
USER_NAME = 'testuser'
USER_NAME_FOLLOWER = 'testuser_follower'
USER_NAME_NOT_FOLLOWER = 'testuser_not_follower'
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


class BaseViewsTests(TestCase):
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
        cls.url_address_map = {
            'index': reverse('posts:index'),
            'follow_index': reverse('posts:follow_index'),
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
            'add_comment': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ),
            'profile_follow': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
            'profile_unfollow': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
        }
        cls.url_templation_map = {
            cls.url_address_map['index']: 'posts/index.html',
            cls.url_address_map['follow_index']: 'posts/follow.html',
            cls.url_address_map['group_list']: 'posts/group_list.html',
            cls.url_address_map['profile']: 'posts/profile.html',
            cls.url_address_map['post_detail']: 'posts/post_detail.html',
            cls.url_address_map['post_create']: 'posts/create_post.html',
            cls.url_address_map['post_edit']: 'posts/create_post.html',
            cls.url_address_map['add_comment']: 'posts/post_detail.html',
            cls.url_address_map['profile_follow']: 'posts/profile.html',
            cls.url_address_map['profile_unfollow']: 'posts/profile.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()


class ViewsTests(BaseViewsTests):

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_test(self, first_object, equiv_object):
        """Проверка верного содержания поста"""
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
                cache.clear()
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_views_index_correct_content(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
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
                cache.clear()
                response = self.authorized_client.get(name)
                first_object = response.context['page_obj'][0]
                self.post_test(first_object, post_one)
        response = self.authorized_client.get(
            self.url_address_map['group_list']
        )
        first_object = response.context['page_obj'][0]
        self.assertNotEqual(first_object.group.title, post_one.group.title)
        self.assertNotEqual(first_object.text, post_one.text)

    def test_views_cash_to_index_page(self):
        """Проверка верного кеширования страници index"""
        index = self.url_address_map['index']
        post_one = Post.objects.create(
            author=self.user,
            text=POST_TEXT_ONE_POST,
            group=self.group_one_post,
            image=self.image_post,
        )
        response = self.authorized_client.get(index)
        post_one.delete()
        cache_response = self.authorized_client.get(index)
        self.assertEqual(response.content, cache_response.content)
        cache.clear()
        response = self.authorized_client.get(index)
        self.assertNotEqual(response.content, cache_response.content)

    def test_views_add_comment_authorized_client_correct(self):
        """Добавление коментария работает с правильным контекстом"""
        response = self.authorized_client.get(
            self.url_address_map['add_comment']
        )
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_views_following_authorized_client_correct(self):
        """
        Верное отображение постов у потписаного и не потписаного пользователя
        """
        follower = User.objects.create_user(username=USER_NAME_FOLLOWER)
        unfollower = User.objects.create_user(username=USER_NAME_NOT_FOLLOWER)
        follower_user = Client()
        unfollower_user = Client()
        follower_user.force_login(follower)
        unfollower_user.force_login(unfollower)
        Follow.objects.create(
            user=follower,
            author=self.user,
        )
        response = follower_user.get(self.url_address_map['follow_index'])
        self.assertTrue(response.context.get('page_obj'))
        response = unfollower_user.get(self.url_address_map['follow_index'])
        self.assertFalse(response.context.get('page_obj'))

    def views_profile_follow_authorized_client_correct(self):
        """Проверка возможности потписаться на пользователя"""
        follower = User.objects.create_user(username=USER_NAME_FOLLOWER)
        follower_user = Client()
        follower_user.force_login(follower)
        self.follower_user.get(
            self.url_address_map['profile_follow']
        )
        self.assertTrue(follower.follower.filter(author=self.user).exists())

    def views_profile_unfollow_authorized_client_correct(self):
        """Проверка возможности отпотписаться на пользователя"""
        follower = User.objects.create_user(username=USER_NAME_FOLLOWER)
        follower_user = Client()
        follower_user.force_login(follower)
        self.follower_user.get(
            self.url_address_map['profile_unfollow']
        )
        self.assertFalse(follower.follower.filter(author=self.user).exists())


class TestPaginator(BaseViewsTests):
    """Тестирование peginator"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for _ in range(settings.SHOW_POST):
            Post.objects.create(
                author=cls.user,
                text=POST_TEXT,
                group=cls.group,
            )
        cls.follower = User.objects.create_user(
            username=USER_NAME_FOLLOWER
        )
        Follow.objects.create(
            user=cls.follower,
            author=cls.user,
        )

    def setUp(self):
        cache.clear()
        self.follower_user = Client()
        self.follower_user.force_login(self.follower)

    def test_views_paginator_first_page_correct(self):
        """Работа peginator первой страници"""
        for name in list(self.url_address_map.values())[:4]:
            with self.subTest(name=name):
                response = self.follower_user.get(name)
                print(len(response.context['page_obj']))
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.SHOW_POST
                )

    def test_views_paginator_second_page_correct(self):
        """Работа peginator следующей страници"""
        for name in list(self.url_address_map.values())[:4]:
            with self.subTest(name=name):
                response = self.follower_user.get(name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    1
                )
