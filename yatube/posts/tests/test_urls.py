from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

USER_NAME = 'testuser'
USER_NAME_NOT_AUTHER = 'notauther'
GROUP_NAME = 'Тестовая група'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.not_auther = User.objects.create_user(
            username=USER_NAME_NOT_AUTHER
        )
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
        cls.access_url_map = {
            cls.url_address_map['index']: ('all', 'authorized'),
            cls.url_address_map['group_list']: ('all', 'authorized'),
            cls.url_address_map['profile']: ('all', 'authorized'),
            cls.url_address_map['post_detail']: ('all', 'authorized'),
            cls.url_address_map['post_create']: ('authorized',),
            cls.url_address_map['post_edit']: ('author',),
        }
        cls.templation_url_map = {
            cls.url_address_map['index']: 'posts/index.html',
            cls.url_address_map['group_list']: 'posts/group_list.html',
            cls.url_address_map['profile']: 'posts/profile.html',
            cls.url_address_map['post_detail']: 'posts/post_detail.html',
            cls.url_address_map['post_create']: 'posts/create_post.html',
            cls.url_address_map['post_edit']: 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_auther_client = Client()
        self.not_auther_client.force_login(self.not_auther)

    def test_urls_correct_templation(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templation_url_map.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """Страницы обработанные для авторизованного пользователя."""
        for address, access in self.access_url_map.items():
            if 'authorized' in access:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_guest_client(self):
        """Страницы обработанные для анонимного пользователя."""
        for address, access in self.access_url_map.items():
            if 'all' in access:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """
        Страницы /create/ и /posts/<post_id>/edit/
        перенаправляющие анонимного пользователя.
        """
        for address, access in self.access_url_map.items():
            if 'all' not in access:
                with self.subTest(address=address):
                    response = self.guest_client.get(address, follow=True)
                    self.assertRedirects(
                        response, (f'/auth/login/?next={address}')
                    )

    def test_urls_redirect_edit_post_on_not_auther(self):
        """
        Страница /posts/<post_id>/edit/ для авторизованного НЕ автора поста.
        """
        for address, access in self.access_url_map.items():
            if 'authorized' not in access:
                with self.subTest(address=address):
                    response = self.not_auther_client.get(address, follow=True)
                    self.assertRedirects(
                        response, (f'/posts/{self.post.pk}/')
                    )

    def test_urls_exists_at_desired_location_on_auther(self):
        """Страница /posts/<post_id>/edit/ для авторизованного автора поста."""
        for address, access in self.access_url_map.items():
            if 'author' in access:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_not_found(self):
        """Корректное отображение несуществующей страници"""
        response_guest = self.guest_client.get("/not_page/")
        self.assertEqual(response_guest.status_code, HTTPStatus.NOT_FOUND)
        response_aut = self.authorized_client.get("/not_page/")
        self.assertEqual(response_aut.status_code, HTTPStatus.NOT_FOUND)
