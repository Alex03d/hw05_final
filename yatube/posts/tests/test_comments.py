import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import User, Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.authorized_user = User.objects.create_user(username='authorized_user')
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author_post,
            text='Тестовый комментарий'
            ),

    def setUp(self):
        self.author_post = Client()
        self.author_post.force_login(PostCommentsTest.author_post)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCommentsTest.authorized_user)

    def test_comment_in_post_detail_page_show_exist(self):
        responses = {
            'post_detail': self.authorized_client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.id}
                )
            )
        }

        for response in responses.values():
            first_object = response.context['comments'][0]
            self.assertIsNotNone(first_object)
            form_object = response.context['form']
            self.assertIsNotNone(form_object)
            self.assertTrue(
                Comment.objects.filter(
                    text='Тестовый комментарий'
                ).exists())

    def test_ability_to_post_a_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Comment check',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count)
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        response = self.client.get(reverse('posts:post_detail',
                                           kwargs={'post_id': self.post.id}
                                           ))
        newly_created_comment = response.context['comments'][0]
        self.assertEqual(str(newly_created_comment), 'Comment check')
