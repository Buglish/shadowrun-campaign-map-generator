from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTestCase(TestCase):
    """Test cases for user registration and login"""

    def setUp(self):
        """Set up test client and test user"""
        self.client = Client()
        self.test_user_data = {
            'username': 'testrunner',
            'email': 'testrunner@example.com',
            'first_name': 'Test',
            'last_name': 'Runner',
            'password1': 'SecureTestPass123!',
            'password2': 'SecureTestPass123!',
        }

    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(reverse('accounts:register'), self.test_user_data)

        # Check user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'testrunner')
        self.assertEqual(user.email, 'testrunner@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'Runner')

        # Check user is automatically logged in and redirected
        self.assertRedirects(response, reverse('home'))

    def test_user_registration_duplicate_email(self):
        """Test that duplicate email addresses are rejected"""
        # Create first user
        self.client.post(reverse('accounts:register'), self.test_user_data)

        # Try to register with same email but different username
        duplicate_data = self.test_user_data.copy()
        duplicate_data['username'] = 'testrunner2'
        response = self.client.post(reverse('accounts:register'), duplicate_data)

        # Should still be on registration page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with this email address already exists.')

        # Only one user should exist
        self.assertEqual(User.objects.count(), 1)

    def test_user_registration_password_mismatch(self):
        """Test that mismatched passwords are rejected"""
        invalid_data = self.test_user_data.copy()
        invalid_data['password2'] = 'DifferentPassword123!'

        response = self.client.post(reverse('accounts:register'), invalid_data)

        # Should still be on registration page
        self.assertEqual(response.status_code, 200)

        # No user should be created
        self.assertEqual(User.objects.count(), 0)

    def test_user_login_success(self):
        """Test successful user login"""
        # Create a user first
        User.objects.create_user(
            username='testrunner',
            email='testrunner@example.com',
            password='SecureTestPass123!'
        )

        # Try to log in
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testrunner',
            'password': 'SecureTestPass123!'
        })

        # Should redirect to home
        self.assertRedirects(response, reverse('home'))

        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Create a user first
        User.objects.create_user(
            username='testrunner',
            password='SecureTestPass123!'
        )

        # Try to log in with wrong password
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testrunner',
            'password': 'WrongPassword'
        })

        # Should stay on login page
        self.assertEqual(response.status_code, 200)

        # User should not be logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_profile_requires_login(self):
        """Test that profile page requires authentication"""
        response = self.client.get(reverse('accounts:profile'))

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts:login')))

    def test_profile_page_loads_for_authenticated_user(self):
        """Test that profile page loads for logged-in users"""
        # Create and log in a user
        user = User.objects.create_user(
            username='testrunner',
            password='SecureTestPass123!'
        )
        self.client.login(username='testrunner', password='SecureTestPass123!')

        response = self.client.get(reverse('accounts:profile'))

        # Should load successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertEqual(response.context['user'], user)

    def test_logout_redirects_to_home(self):
        """Test that logout redirects to home page"""
        # Create and log in a user
        User.objects.create_user(
            username='testrunner',
            password='SecureTestPass123!'
        )
        self.client.login(username='testrunner', password='SecureTestPass123!')

        # Log out (use POST method)
        response = self.client.post(reverse('accounts:logout'))

        # Should redirect to home
        self.assertRedirects(response, reverse('home'))
