import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description'
        )
        cls.group2 = Group.objects.create(
            title='test_title2',
            slug='test_slug2',
            description='test_description2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_create_post_form(self):
        data = {
            'text': 'new_text',
            'group': self.group.pk
        }
        self.user_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True
        )
        self.assertEqual(str(Post.objects.get(id=2)), data['text'],
                         'Форма создания поста работает некорректно'
                         )

    def test_post_edit_form(self):
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        data = {
            'text': 'new_text',
            'group': self.group2.pk
        }

        self.user_client.post(url, data)
        self.post.refresh_from_db()
        self.group.refresh_from_db()
        self.assertEqual(self.post.text, data["text"],
                         'Форма редактирования поста работает некорректно'
                         )
        self.assertNotEqual(self.post.group, self.group.title,
                            'Форма редактирования группы работает некорректно'
                            )

    def test_picture_form(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group2.pk,
            'image': uploaded,
        }
        url = self.user_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(url, reverse('posts:profile',
                             kwargs={'username': self.post.author})
                             )
        self.assertTrue(Post.objects.filter(
                        text='Пост с картинкой',
                        group=self.group2.pk,
                        image='posts/small.gif'
                        ).exists())
        
        
        # self.assertEqual(self.post.image.uploaded, 'posts/small.gif')
