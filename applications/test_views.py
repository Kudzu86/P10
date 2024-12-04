from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class ProjectAPITestCase(APITestCase):
    
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', password='testpass', age=20)
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        data = {
            'title': 'Mon projet',  # Utilise 'title' comme défini dans le serializer ProjectSerializer
            'description': 'Description du projet',
            'contributors': [self.user.id],  # Ajouter l'ID de l'utilisateur comme contributeur
        }
        response = self.client.post('/api/projects/', data, format='json')  # Utilise format='json' pour envoyer des données JSON
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().title, 'Mon projet')  # Assurez-vous de tester avec 'title'

    def test_project_pagination(self):
        # Créer plusieurs projets
        for i in range(15):
            Project.objects.create(title=f'Projet {i}', description='Description', author=self.user, contributors=[self.user])

        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Vérifie que la pagination limite à 10 projets

    def test_create_project_without_contributor(self):
        """
        Test pour s'assurer qu'un projet sans contributeur échoue, si tel est le cas dans votre logique métier.
        """
        data = {
            'title': 'Projet sans contributeur',
            'description': 'Description sans contributeur',
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Si le contributeur est requis
