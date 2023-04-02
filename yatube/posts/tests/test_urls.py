from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import User, Post, Group

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth_user')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test desc',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            pk='2'
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.client = Client()
        self.client.force_login(self.user)

    def test_post_name_guest(self):
        url_guest = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for address, template in url_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if address == '/unexisting_page/':
                    self.assertEqual(response.status_code, 404)
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, template)

    def test_client(self):
        url_authorized = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in url_authorized.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
