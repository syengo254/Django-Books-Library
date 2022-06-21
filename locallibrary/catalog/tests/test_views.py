import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission

from catalog.models import Author, User

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authors/list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['authors']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['authors']), 3)



class AuthorCreateViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='password123!')
        test_user2 = User.objects.create_user(username='testuser2', password='password123!')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='password123!')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_create_form_is_properly_displayed_on_get_request(self):
        self.client.login(username='testuser2', password='password123!')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form action="" method="post">')

    def test_correct_template_is_used(self):
        self.client.login(username='testuser2', password='password123!')
        response = self.client.get(reverse('author-create'))
        self.assertTemplateUsed(response, 'authors/author_form.html')
    
    def test_date_of_death_field_is_initially_correct_value(self):
        self.client.login(username='testuser2', password='password123!')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

        expected_val = datetime.date(2022, 6, 11)
        response_date = response.context['form'].initial['date_of_death']
        response_date = datetime.datetime.strptime(response_date, "%d/%m/%Y").date()
        self.assertEqual(response_date, expected_val)
    
    def test_redirects_to_detail_view_on_success(self):
        self.client.login(username='testuser2', password='password123!')
        response = self.client.post(reverse('author-create'),
                                    {'first_name': 'Christian Name', 'last_name': 'Surname'})

        # Manually check redirect because we don't know what author was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/authors/'))