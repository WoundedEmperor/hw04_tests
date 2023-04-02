# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        Post.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='sluggy-slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group,
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='TestUsername')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def post_exist(self, page_context):
        """Метод проверки существования поста на страницах."""
        if 'page_obj' in page_context:
            post = page_context['page_obj'][0]
        else:
            post = page_context['post']
        task_author = post.author
        task_text = post.text
        task_group = post.group
        self.assertEqual(
            task_author,
            PostPagesTests.post.author
        )
        self.assertEqual(
            task_text,
            PostPagesTests.post.text
        )
        self.assertEqual(
            task_group,
            PostPagesTests.post.group
        )
        self.assertEqual(
            post.comments.last(),
            PostPagesTests.comment_post
        )

    def test_paginator_correct_context(self):
        """Шаблон index, group_list и profile
        сформированы с корректным Paginator.
        """
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostPagesTests.user,
                text='Тестовый пост ' + str(i),
                group=PostPagesTests.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    8
                )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response_index = self.authorized_client.get(reverse('posts:index'))
        page_index_context = response_index.context
        self.post_exist(page_index_context)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.pk}
            )
        )
        page_post_detail_context = response_post_detail.context
        self.post_exist(page_post_detail_context)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        page_group_context = response_group.context
        task_group = response_group.context['group']
        self.post_exist(page_group_context)
        self.assertEqual(task_group, PostPagesTests.group)

    def test_profile_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username}
            )
        )
        page_profile_context = response_profile.context
        task_profile = response_profile.context['author']
        self.post_exist(page_profile_context)
        self.assertEqual(task_profile, PostPagesTests.user)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
