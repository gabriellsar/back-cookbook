from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from infra.models import CustomUser, Recipe, Step

class StepPermissionsTests(APITestCase):
    def setUp(self):
        self.guardian = CustomUser.objects.create_user(username='guardian_step', password='123')
        self.heir = CustomUser.objects.create_user(username='heir_step', password='123')

        # Raiz e Fork
        self.root_recipe = Recipe.objects.create(author=self.guardian, title='Root', description='...')
        self.forked_recipe = Recipe.objects.create(author=self.heir, title='Fork', description='...', forked_from=self.root_recipe)
        
        # Passos
        self.locked_step_fork = Step.objects.create(recipe=self.forked_recipe, order=1, instruction='Segredo', is_locked=True)

    def test_heir_cannot_modify_locked_step(self):
        """Garante que a mesma proteção aplicada aos ingredientes funciona para os Passos"""
        self.client.force_authenticate(user=self.heir)
        url = reverse('step-detail', kwargs={'pk': self.locked_step_fork.id})
        
        # Tentativa de Atualizar
        patch_response = self.client.patch(url, {'instruction': 'Hacker'})
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Tentativa de Deletar
        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)