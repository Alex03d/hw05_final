from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User
from ..forms import PostForm


class PostFormTexts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.guest_user = User.objects.create_user(username='Auth')
        self.client.force_login(self.guest_user)

    def test_create_post(self):
        group = Group.objects.create(
            title='Тестовая группа для отправки',
            slug='test-slug-post',
            description='Тестовое описание группы не более 15 символов'
        )
        posts_count = Post.objects.count()
        form_data_before = {
            'text': 'Тестовый заголовок для валидации',
            'author': User.objects.filter(username='Auth'),
            'group': group.id
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data_before,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок для валидации',
                id=1,
            ).exists()
        )
