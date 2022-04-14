from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.views import POSTS_PER_PAGE

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
        )
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='TestDescription',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_template(self):
        template_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': PostPagesTests.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.post.author}
            ),
            'posts/create_post.html/': reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTests.post.pk}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTests.post.pk}
            ),
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_template_create_post(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html/')

    def test_context_index(self):
        for x in range(13):
            Post.objects.create(text=f'text{x}', author=PostPagesTests.user)
        url = reverse('posts:index')
        r = self.guest_client.get(url)
        page_obj = r.context.get('page_obj')
        self.assertEqual(len(page_obj),
                         POSTS_PER_PAGE,
                         'Пагинатор работает некорректно'
                         )

    def test_context_group_list(self):
        for x in range(13):
            Post.objects.create(
                text=f'text{x}',
                author=PostPagesTests.user,
                group=PostPagesTests.group,
            )
        url = reverse('posts:group_list',
                      kwargs={'slug': PostPagesTests.group.slug}
                      )
        r = self.guest_client.get(url)
        page_obj = r.context.get('page_obj')
        group = r.context.get('group')
        self.assertEqual(len(page_obj),
                         POSTS_PER_PAGE,
                         'Пагинатор работает некорректно'
                         )
        self.assertEqual(str(group),
                         PostPagesTests.group.title,
                         'Отображение группы некорректно'
                         )

    def test_context_profile(self):
        for x in range(13):
            Post.objects.create(
                text=f'text{x}',
                author=PostPagesTests.user,
            )
        url = reverse('posts:profile',
                      kwargs={'username': PostPagesTests.post.author}
                      )
        r = self.guest_client.get(url)
        page_obj = r.context.get('page_obj')
        author = r.context.get('author')
        self.assertEqual(len(page_obj),
                         POSTS_PER_PAGE,
                         'Пагинатор работает некорректно'
                         )
        self.assertEqual(author,
                         PostPagesTests.user,
                         'Отображение автора некорректно'
                         )

    def test_context_post_detail(self):
        url = reverse('posts:post_detail',
                      kwargs={'post_id': PostPagesTests.post.pk}
                      )
        r = self.guest_client.get(url)
        post = r.context.get('post')
        self.assertEqual(post,
                         PostPagesTests.post,
                         'Отображение поста некорректно'
                         )

    def test_context_edit_post(self):
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        r = self.authorized_client.get(url)
        form = r.context.get('form')
        is_edit = r.context.get('is_edit')
        post_id = r.context.get('post_id')
        self.assertEqual(form.instance,
                         self.post,
                         'Отображение form некоректно'
                         )
        self.assertTrue(is_edit,
                        'Отображение is_edit некорректно'
                        )
        self.assertEqual(post_id,
                         self.post.pk,
                         'Отображение post_id некорректно'
                         )

    def test_context_create_post(self):
        url = reverse('posts:post_create')
        new_text = 'new_text'
        data = dict(
            text=new_text
        )
        self.authorized_client.post(url, data=data)
        self.post.refresh_from_db()
