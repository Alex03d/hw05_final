from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group, User, Follow


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.authorized_user = User.objects.create_user(
            username='authorized_user')
        cls.subscribed_user = User.objects.create_user(
            username='subscribed_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Текстовый пост',
        )

    def setUp(self):
        self.author_post = Client()
        self.author_post.force_login(PostViewTest.author_post)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.authorized_user)
        self.subscribed_user = Client()
        self.subscribed_user.force_login(PostViewTest.subscribed_user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = [
            ('posts/index.html',
             reverse('posts:index')),
            ('posts/group_list.html',
             reverse('posts:group_posts', kwargs={'slug': 'test-slug'})),
            ('posts/profile.html',
             reverse(
                 'posts:profile',
                 kwargs={'username': self.post.author.username})
             ),
            ('posts/post_detail.html',
             reverse('posts:post_detail', kwargs={'post_id': self.post.id})),
            ('posts/create_post.html',
             reverse('posts:post_edit', kwargs={'post_id': self.post.id})),
            ('posts/create_post.html', reverse('posts:post_create'))]

        for template, reverse_name in templates_pages_names:
            return template, reverse_name
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_correct_context(self):
        response = self.author_post.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_appearance(self):
        Post.objects.create(
            text='Текстовый пост с группой',
            author=User.objects.get(username='author_post'),
            group=Group.objects.get(
                title='Тестовая группа',
            )
        )
        responses = {
            'index': self.authorized_client.get(
                reverse('posts:index')),
            'group_posts': self.authorized_client.get(
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': 'test-slug'})),
            'profile': self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': 'author_post'}))
        }
        for response in responses.values():
            inner_response = response
            first_object = inner_response.context['page_obj'][0]
            post_text_0 = first_object.text
            post_author_0 = first_object.author
            post_group_0 = first_object.group
            self.assertEqual(post_text_0, 'Текстовый пост с группой')
            self.assertEqual(
                post_author_0,
                User.objects.get(username='author_post'),
            )
            self.assertEqual(
                post_group_0,
                Group.objects.get(
                    title='Тестовая группа',
                )
            )

    def test_cache_index_page(self):
        first_look = self.authorized_client.get(
            reverse('posts:index'))
        Post.objects.create(
            text='Текст тестировки кэша',
            author=User.objects.get(username='author_post'),
        )
        second_look = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(first_look.content, second_look.content)
        cache.clear()
        third_look = self.authorized_client.get(
            reverse('posts:index'))
        self.assertNotEqual(first_look.content, third_look.content)

    def test_follow_function(self):
        Follow.objects.create(
            user=User.objects.get(username='subscribed_user'),
            author=User.objects.get(username='author_post'))
        followers_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'author_post'}))
        self.assertEqual(Follow.objects.count(), followers_count + 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'author_post'}))
        self.assertEqual(Follow.objects.count(), followers_count)

    def test_appearance_of_followed_authors_posts(self):
        Follow.objects.create(
            user=User.objects.get(username='subscribed_user'),
            author=User.objects.get(username='author_post'))
        Post.objects.create(
            text='Тест подписок',
            author=User.objects.get(username='author_post'),
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'author_post'}))
        response_for_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        followed_post = response_for_follower.context['page_obj'][0]
        self.assertEqual(str(followed_post), 'Тест подписок')
        response_for_not_follower = self.client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(str(followed_post), response_for_not_follower)
