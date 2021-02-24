from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
Group = get_user_model()


class Post(models.Model):
    text = models.TextField('Текст', help_text='Напишите свой прекрасный пост')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = (models.ForeignKey(User, on_delete=models.CASCADE,
              related_name='posts', verbose_name='Автор'))
    group = (models.ForeignKey('Group', on_delete=models.SET_NULL,
             related_name='posts', verbose_name='Группа',
             help_text='Выберите группу из списка (необязательно)',
             blank=True, null=True))
    image = (models.ImageField(upload_to='posts/', blank=True, null=True,
             verbose_name='Картинка', help_text='Загрузите картинку'))

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.fields.SlugField('Ссылка', unique=True)
    description = models.TextField('Описание группы')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = (models.ForeignKey('Post', on_delete=models.CASCADE,
            related_name='comments', verbose_name='Текст поста',
            blank=True, null=True))
    author = (models.ForeignKey(User, on_delete=models.CASCADE,
              related_name='comments', verbose_name='Автор'))
    text = models.TextField('Комментарий', help_text='Прокомментируйте пост')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = (models.ForeignKey(User, on_delete=models.CASCADE,
            related_name='follower', verbose_name='Подписчик'))
    author = (models.ForeignKey(User, on_delete=models.CASCADE,
              related_name='following', verbose_name='Автор'))

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_following'
        )
