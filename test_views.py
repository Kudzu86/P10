from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from projects.models import Project

class UserTests(APITestCase):
    def setUp(self):
        # Création d'un utilisateur de test
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        data = {'username': 'newuser', 'password': 'testpassword'}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# Tests pour Projects
class ProjectTests(APITestCase):
    def setUp(self):
        # Création d'un utilisateur et d'un projet de test
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(title='Test Project', description='Test Description', author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        data = {'title': 'New Project', 'description': 'Project Description'}
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# Tests pour Issues
class IssueTests(APITestCase):
    def setUp(self):
        # Créer un utilisateur, un projet et un problème
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(title='Test Project', description='Test Description', author=self.user)
        self.issue = Issue.objects.create(title='Test Issue', project=self.project, author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_issue(self):
        data = {'title': 'New Issue', 'description': 'Issue Description', 'project': self.project.id}
        response = self.client.post('/api/issues/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)