from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Test_User", )
        cls.group = Group.objects.create(
            title="тест-группа",
            slug="test_group",
            description="тестирование",
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=Group.objects.get(slug='test_group'),
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username="Test_User")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.client.get(template)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        templates = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'Test_User'}),
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}),
        ]
        for template in templates:
            with self.subTest(template=template):
                response = self.client.get(template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
