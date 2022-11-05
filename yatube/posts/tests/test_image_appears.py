import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        author_post = User.objects.create_user(username='author_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=author_post,
            group=Group.objects.get(
                title='Тестовая группа',
            ),
            image=uploaded,
        )

    def test_post_create_correct_appearance_of_image(self):
        responses = {
            'index': self.client.get(
                reverse('posts:index')),
            'profile': self.client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': 'author_post'})),
            'group_posts': self.client.get(
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': 'test-slug'})),
        }
        for response in responses.values():
            first_object = response.context['page_obj'][0]
            post_image = first_object.image
            self.assertIsNotNone(post_image)

        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id})
        )
        only_object = response.context['post_info']
        post_image = only_object.image
        self.assertIsNotNone(post_image)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
