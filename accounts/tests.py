# accounts/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Profile
from django.conf import settings
from accounts.forms import CustomSignupForm, CustomLoginForm, ProfileInfoForm, AddressForm
import json


class RegistrationViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')
        self.data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }

    def test_registration_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_registration_view_post_success(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_registration_view_post_invalid(self):
        self.data['password2'] = 'wrongpassword'
        response = self.client.post(self.url, self.data)

        # Check that the response is a 200 OK, meaning the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the form with errors
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

        # Ensure the form error for 'password2' field
        self.assertFormError(response, 'form', 'password2', 'The two password fields didn’t match.')


class CustomLoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post_success(self):
        response = self.client.post(self.url, {'username': 'testuser@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_view_post_invalid(self):
        response = self.client.post(self.url, {'username': 'testuser@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')


class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.url = reverse('profile')

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser@example.com', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile_detail.html')
        self.assertEqual(response.context['user'], self.user)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("login")}?next={self.url}')


class AddressUpdateViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.url = reverse('address-update')
        self.data = {
            'address_city': 'Test City',
            'address_country': 'US',
            'address_line1': '123 Test St',
            'address_line2': 'Apt 1',
            'address_postal_code': '12345',
            'address_state': 'Test State'
        }

    def test_address_update_view_authenticated(self):
        self.client.login(username='testuser@example.com', password='testpassword')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.address_city, 'Test City')

    def test_address_update_view_unauthenticated(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 404)
        self.assertRedirects(response, f'{reverse("login")}?next={self.url}', status_code=302)


class ProfileInfoUpdateViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.url = reverse('profile-info-update')
        self.data = {
            'name': 'New Name',
            'email': 'newemail@example.com',
            'phone': '1234567890'
        }

    def test_profile_info_update_view_authenticated(self):
        self.client.login(username='testuser@example.com', password='testpassword')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'New Name')
        self.assertEqual(self.profile.email, 'newemail@example.com')

    def test_profile_info_update_view_unauthenticated(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 404)
        self.assertRedirects(response, f'{reverse("login")}?next={self.url}')
