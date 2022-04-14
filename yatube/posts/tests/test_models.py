from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_str(self):
        post = PostModelTest.post
        result = str(post)
        self.assertEqual(result,
                         post.text[:15],
                         'некоректное отображение текста поста'
                         )

    def test_str_group(self):
        group = PostModelTest.group.title
        result = str(group)
        self.assertEqual(result,
                         group,
                         'некоректное отображение названия группы'
                         )
