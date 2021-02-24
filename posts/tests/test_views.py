import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
            description='Тестовое описание_2',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(username='Тестовый автор'),
            group=Group.objects.get(title=cls.group.title),
            image=cls.uploaded,
        )

        cls.user_2 = User.objects.create(username='Тестовый автор_2')
        cls.user_3 = User.objects.create(username='Тестовый автор_3')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': self.group.slug}),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), Post.objects.count())

        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = (self.authorized_client.get(
                    reverse('group', kwargs={'slug': self.group.slug})))
        (self.assertEqual(len(response.context['page']),
         self.group.posts.count()))
        self.assertEqual(response.context.get('group'), self.group)

        response = (self.authorized_client.get(
                    reverse('group', kwargs={'slug': self.group_2.slug})))
        (self.assertEqual(len(response.context['page']),
         self.group_2.posts.count()))
        self.assertEqual(response.context.get('group'), self.group_2)

    def test_post_with_group_exists_on_index(self):
        """Созданный пост существует на главной странице"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), Post.objects.count())

        post_text_0 = response.context.get('page')[0].text
        self.assertIn('Тестовый текст', post_text_0)

    def test_post_with_group_exists_on_correct_group(self):
        """Созданный пост c фото существует на странице выбранной группы"""
        response = (self.authorized_client.get(
                    reverse('group', kwargs={'slug': self.group.slug})))
        (self.assertEqual(len(response.context['page']),
         self.group.posts.count()))
        post_text_0 = response.context.get('page')[0].text
        post_image_0 = response.context.get('page')[0].image
        self.assertIn('Тестовый текст', post_text_0)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_with_group_does_not_exist_on_incorrect_group(self):
        """Созданный пост не существует на странице невыбранной группы"""
        response = (self.authorized_client.get(
                    reverse('group', kwargs={'slug': self.group_2.slug})))
        (self.assertEqual(len(response.context['page']),
         self.group_2.posts.count()))

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом"""
        form_data = {
            'text': 'Тестовый текст_2',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(len(response.context['page']), Post.objects.count())
        post_text_0 = response.context.get('page')[0].text
        self.assertEqual(post_text_0, form_data['text'])

        response = (self.authorized_client.get(
                    reverse('group', kwargs={'slug': self.group_2.slug})))
        (self.assertEqual(len(response.context['page']),
         self.group_2.posts.count()))
        post_text_0 = response.context.get('page')[0].text
        self.assertEqual(post_text_0, form_data['text'])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = (self.authorized_client.get(
                    reverse('profile', kwargs={'username': self.post.author})))
        author = self.post.author
        self.assertEqual(len(response.context['page']), author.posts.count())

        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_post__view_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = (self.authorized_client.get(
                    reverse('post', kwargs={'username': self.post.author,
                            'post_id': self.post.id})))

        post_text = response.context.get('post').text
        post_author = response.context.get('post').author
        post_group = response.context.get('post').group
        post_image = response.context.get('post').image
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_image, self.post.image)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        form_data = {
            'text': 'Тестовый текст_edit',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': self.post.author,
                                         'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.post.refresh_from_db()

        post_text = response.context.get('post').text
        self.assertEqual(post_text, form_data['text'])

    def test_cache_works_on_index_page(self):
        """Кэш работает на странице index"""
        response_before_post = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Тестовый текст_2',
            author=self.post.author,
        )
        response_after_post = self.authorized_client.get(reverse('index'))
        (self.assertEqual(response_before_post.content,
                          response_after_post.content))
        cache.clear()
        response_after_clear = self.authorized_client.get(reverse('index'))
        (self.assertNotEqual(response_before_post.content,
                             response_after_clear.content))

    def test_authorized_client_can_follow_other_users(self):
        """Авторизованный пользователь может подписываться на
        других пользователей"""
        self.assertEqual(self.user_2.following.count(), 0)
        self.assertEqual(self.post.author.follower.count(), 0)
        (self.authorized_client.get(reverse('profile_follow',
                                    kwargs={'username': self.user_2})))
        self.assertEqual(self.user_2.following.count(), 1)
        self.assertEqual(self.post.author.follower.count(), 1)

    def test_authorized_client_can_unfollow_other_users(self):
        """Авторизованный пользователь может отписываться от
        других пользователей"""
        (self.authorized_client.get(reverse('profile_follow',
                                    kwargs={'username': self.user_2})))
        (self.authorized_client.get(reverse('profile_unfollow',
                                    kwargs={'username': self.user_2})))
        self.assertEqual(self.user_2.following.count(), 0)
        self.assertEqual(self.post.author.follower.count(), 0)

    def test_new_post_appears_on_followindex_at_the_subscriber(self):
        """Новая запись пользователя появляется в ленте у подписчика"""
        (self.authorized_client.get(reverse('profile_follow',
                                    kwargs={'username': self.user_2})))
        post_user_2 = Post.objects.create(
            text='Тестовый текст_2',
            author=self.user_2,
        )
        response = self.authorized_client.get(reverse('follow_index'))
        (self.assertEqual(len(response.context['page']),
                          post_user_2.author.posts.count()))
        post_text_0 = response.context.get('page')[0].text
        self.assertIn(post_user_2.text, post_text_0)

    def test_new_post_absent_on_follow_index_at_the_not_subscriber(self):
        """Новая запись не появляется в ленте у не подписчика"""
        Post.objects.create(
            text='Тестовый текст_3',
            author=self.user_3,
        )
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='Тестовый автор')

        for text in range(13):
            Post.objects.create(
                text=text,
                author=cls.user,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_page1_list_is_10(self):
        """На 1-ю страницу index передается 10 постов"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 10)

    def test_post_page2_list_is_3(self):
        """На 2-ю страницу index передается 3 поста"""
        response = self.authorized_client.get(reverse('index') + '?page=2')
        (self.assertEqual(len(response.context['page']),
                          len(Post.objects.all()) - 10))
