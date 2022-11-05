from django.test import TestCase, Client

from ..models import Post, Group, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.simple_user = User.objects.create_user(username='simple_user')
        cls.group = Group.objects.create(
            title='Тестовая гурппа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.simple_user)
        self.author_post = Client()
        self.author_post.force_login(PostURLTest.author_post)

    def test_urls_uses_correct_template_authorized(self):
        url_templates_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{PostURLTest.post.id}/': 'posts/post_detail.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_redirect_if_not_authorized(self):
        url_templates_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{PostURLTest.post.id}/edit/':
                f'/auth/login/?next=/posts/{PostURLTest.post.id}/edit/',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, template)

    def test_urls_uses_correct_template_if_author(self):
        url_templates_names = {
            f'/posts/{PostURLTest.post.id}/edit/': 'posts/create_post.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.author_post.get(address)
                self.assertTemplateUsed(response, template)
