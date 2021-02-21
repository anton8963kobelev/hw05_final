from django.test import TestCase

from posts.models import Group, Post, User, Comment, Follow


class AllModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(username='Тестовый автор'),
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.comment = Comment.objects.create(
            post=Post.objects.get(text=cls.post.text),
            author=cls.post.author,
            text='Тестовый комментарий',
        )

        cls.follow = Follow.objects.create(
            user=User.objects.create(username='Тестовый автор_2'),
            author=cls.post.author,
        )

    def test_model_post_verbose_names(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = AllModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_model_group_verbose_names(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = AllModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Ссылка',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_model_comment_verbose_names(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = AllModelTest.comment
        field_verboses = {
            'post': 'Текст поста',
            'author': 'Автор',
            'text': 'Комментарий',
            'created': 'Дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_model_follow_verbose_names(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = AllModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_model_post_help_texts(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = AllModelTest.post
        field_help_texts = {
            'text': 'Напишите свой прекрасный пост',
            'group': 'Выберите группу из списка (необязательно)',
            'image': 'Загрузите картинку',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_model_comment_help_texts(self):
        """help_text в полях модели Comment совпадает с ожидаемым."""
        comment = AllModelTest.comment
        expected = 'Прокомментируйте пост'
        self.assertEqual(comment._meta.get_field('text').help_text, expected)

    def test_object_name_is_text_fild(self):
        """В поле __str__  объекта post записано
        значение поля post.text[:15]."""
        post = AllModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = AllModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
