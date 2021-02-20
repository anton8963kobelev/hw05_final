from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(username='AntonK'),
        )

        cls.post_2 = Post.objects.create(
            text='Тестовый текст_2',
            author=User.objects.create(username='stranger'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_slugs = [
            '/',
            f'/group/{self.group.slug}',
            f'/{self.post.author}/',
            f'/{self.post.author}/{self.post.id}/',
        ]
        for slug in url_slugs:
            with self.subTest():
                response = self.guest_client.get(slug)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        (self.assertRedirects(response, reverse('login') + '?next='
                              + reverse('new_post')))

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/edit/
        доступна авторизованному автору поста."""
        response = (self.authorized_client.get(
                    f'/{self.post.author}/{self.post.id}/edit/'))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /<username>/<post_id>/edit/
        перенаправит анонимного пользователя на страницу логина."""
        response = (self.guest_client.get(
                    f'/{self.post.author}/{self.post.id}/edit/',
                    follow=True))
        (self.assertRedirects(response, reverse('login') + '?next='
                              + reverse('post_edit', kwargs={
                                        'username': self.post.author,
                                        'post_id': self.post.id})))

    def test_post_edit_url_redirect_non_author_of_the_post(self):
        """Страница по адресу /<username>/<post_id>/edit/
        перенаправит не автора поста на страницу просмотра поста."""
        response = (self.authorized_client.get(
                    f'/{self.post_2.author}/{self.post_2.id}/edit/',
                    follow=True))
        self.assertRedirects(response, reverse('post', kwargs={
                                               'username': self.post_2.author,
                                               'post_id': self.post_2.id}))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': f'/group/{self.group.slug}',
            'new.html': '/new/',
            'profile.html': f'/{self.post.author}/',
            'post.html': f'/{self.post.author}/{self.post.id}/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        """/<username>/<post_id>/edit/ использует шаблон new.html."""
        response = (self.authorized_client.get(
                    f'/{self.post.author}/{self.post.id}/edit/'))
        self.assertTemplateUsed(response, 'new.html')

    def test_code_404_if_page_is_not_found(self):
        """Сервет возвращает код 404, если страница не найдена"""
        response = self.authorized_client.get('/group/')
        self.assertEqual(response.status_code, 404)
