from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post, Group, User
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostFormTests(TestCase):
    """Создаем тестовые посты, группу и форму."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='testslug',
            description='Описание'
        )
        cls.new_group = Group.objects.create(
            title='Новый заголовок',
            slug='newslug',
            description='Новое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Старый пост',
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_fields = {
            'text': 'test text',
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test text1',
            'group': self.new_group.id,
        }
        response = self.client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True,
        )

        """response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}),
            data=form_data['text'],
            follow=True,
        )"""
        mod_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(1,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(
            mod_post.text,
            self.post.text,
            'text не изменился'
        )
        self.assertNotEqual(
            mod_post.group,
            self.post.group,
            'group не изменилась'
        )
