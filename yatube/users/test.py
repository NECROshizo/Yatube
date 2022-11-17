from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()
USER_NAME = 'testuser'


class BaseTestUsers(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)


class BaseTestUsers(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.url_address_map = {
            'signup': reverse('users:signup'),
            'logout': reverse('users:logout'),
            'login': reverse('users:login'),
            'pass_reset': reverse('users:password_reset_form'),
            'pass_reset_done': reverse('users:password_reset_done'),
            'pass_change': reverse('users:password_change'),
            'pass_change_done': reverse('users:password_change_done'),
            'email_confirm_link': '/auth/reset/<uidb64>/<token>/',
            'pass_confirm_done': reverse('users:password_reset_complete'),
        }
        cls.access_url_map = {
            cls.url_address_map['signup']: ('guest', 'authorized'),
            cls.url_address_map['login']: ('guest', 'authorized'),
            cls.url_address_map['pass_reset']: ('guest', 'authorized',),
            cls.url_address_map['pass_reset_done']: ('guest', 'authorized'),
            cls.url_address_map['pass_change']: ('authorized',),
            cls.url_address_map['pass_change_done']: ('authorized',),
            cls.url_address_map['email_confirm_link']:
                ('guest', 'authorized',),
            cls.url_address_map['pass_confirm_done']: ('guest', 'authorized'),
            cls.url_address_map['logout']: ('guest', 'authorized'),
        }


class URLTest(BaseTestUsers):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templation_url_map = {
            cls.url_address_map['signup']: 'users/signup.html',
            cls.url_address_map['login']: 'users/login.html',
            cls.url_address_map['pass_reset']:
                'users/password_reset_form.html',
            cls.url_address_map['pass_reset_done']:
                'users/password_reset_done.html',
            cls.url_address_map['pass_change']:
                'users/password_change_form.html',
            cls.url_address_map['pass_change_done']:
                'users/password_change_done.html',
            cls.url_address_map['email_confirm_link']:
                'users/password_reset_confirm.html',
            cls.url_address_map['pass_confirm_done']:
                'users/password_reset_complete.html',
            cls.url_address_map['logout']: 'users/logged_out.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_correct_templation(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templation_url_map.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
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
            if 'guest' in access:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправляющие анонимного пользователя yf регистрацию."""
        for address, access in self.access_url_map.items():
            if 'guest' not in access:
                with self.subTest(address=address):
                    response = self.guest_client.get(address, follow=True)
                    self.assertRedirects(
                        response, (f'/auth/login/?next={address}')
                    )


class FormTest(BaseTestUsers):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        """Создаем пользователя"""
        users_count = User.objects.count()
        form_user = {
            'first_name': 'Саруман',
            'last_name': 'Белый',
            'username': 'TrueWhiteWizard',
            'email': 'Wizard@mordor.ru',
            'password1': 'Gandalfloser!',
            'password2': 'Gandalfloser!'
        }
        response = self.guest_client.post(
            reverse(self.url_address_map['signup']),
            data=form_user,
            follow=True,
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/')


class ViewsTest(BaseTestUsers):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_correct_content(self):
        response = self.authorized_client.get(self.url_address_map['signup'])
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
