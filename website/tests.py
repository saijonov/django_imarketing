from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
import shutil
from .models import Application
from .forms import ApplicationForm
from bot.models import Vacancy, VacancyField
import json
import tempfile

# Create a temp media root for test files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class WebsiteTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        # Create a test image
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image = SimpleUploadedFile('test_image.gif', self.image_content, content_type='image/gif')
        
        # Create a test vacancy
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            short_text_uz='Test short UZ',
            short_text_ru='Test short RU',
            full_text_uz='Test full UZ',
            full_text_ru='Test full RU',
            image=self.image,
            is_published=True
        )
        
        # Create custom fields for the vacancy
        self.field1 = VacancyField.objects.create(
            vacancy=self.vacancy,
            name='experience',
            label_uz='Tajriba',
            label_ru='Опыт',
            field_type='text',
            required=True,
            order=1
        )
        
        self.field2 = VacancyField.objects.create(
            vacancy=self.vacancy,
            name='skills',
            label_uz='Ko\'nikmalar',
            label_ru='Навыки',
            field_type='text',
            required=False,
            order=2
        )

    def tearDown(self):
        """Clean up test files"""
        try:
            shutil.rmtree(TEMP_MEDIA_ROOT)
        except Exception as e:
            print(f'Error while deleting temp directory: {e}')

    def test_vacancy_list_view(self):
        """Test vacancy list view with different languages"""
        # Test Uzbek
        response_uz = self.client.get(reverse('vacancy_list') + '?lang=uz')
        self.assertEqual(response_uz.status_code, 200)
        self.assertContains(response_uz, 'Test short UZ')
        
        # Test Russian
        response_ru = self.client.get(reverse('vacancy_list') + '?lang=ru')
        self.assertEqual(response_ru.status_code, 200)
        self.assertContains(response_ru, 'Test short RU')

    def test_vacancy_detail_view(self):
        """Test vacancy detail view with different languages"""
        # Test Uzbek
        response_uz = self.client.get(reverse('vacancy_detail', args=[self.vacancy.id]) + '?lang=uz')
        self.assertEqual(response_uz.status_code, 200)
        self.assertContains(response_uz, 'Test full UZ')
        self.assertContains(response_uz, 'Tajriba')
        
        # Test Russian
        response_ru = self.client.get(reverse('vacancy_detail', args=[self.vacancy.id]) + '?lang=ru')
        self.assertEqual(response_ru.status_code, 200)
        self.assertContains(response_ru, 'Test full RU')
        self.assertContains(response_ru, 'Опыт')

    def test_application_form_submission(self):
        """Test submitting an application form"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+998901234567',
            'cover_letter': 'Test cover letter',
            f'custom_{self.field1.id}': 'Test experience',
            f'custom_{self.field2.id}': 'Test skills'
        }
        
        response = self.client.post(
            reverse('vacancy_detail', args=[self.vacancy.id]) + '?lang=uz',
            data=form_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Application.objects.filter(name='Test User').exists())
        
        # Check if answers are saved correctly
        application = Application.objects.get(name='Test User')
        self.assertEqual(
            application.answers.get(str(self.field1.id)),
            'Test experience'
        )

    def test_application_form_validation(self):
        """Test form validation"""
        # Test with missing required field
        form_data = {
            'name': 'Test User',
            'email': 'invalid-email',  # Invalid email
            'phone': '+998901234567',
            'cover_letter': 'Test cover letter',
            f'custom_{self.field2.id}': 'Test skills'
            # Missing required field1
        }
        
        form = ApplicationForm(data=form_data, vacancy=self.vacancy)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn(f'custom_{self.field1.id}', form.errors)

    def test_form_language_labels(self):
        """Test form field labels in different languages"""
        # Test Uzbek labels
        form_uz = ApplicationForm(vacancy=self.vacancy, language='uz')
        self.assertEqual(form_uz.fields['name'].label, 'To\'liq ism')
        self.assertEqual(form_uz.fields[f'custom_{self.field1.id}'].label, 'Tajriba')
        
        # Test Russian labels
        form_ru = ApplicationForm(vacancy=self.vacancy, language='ru')
        self.assertEqual(form_ru.fields['name'].label, 'ФИО')
        self.assertEqual(form_ru.fields[f'custom_{self.field1.id}'].label, 'Опыт')

    def test_unpublished_vacancy(self):
        """Test that unpublished vacancies are not accessible"""
        self.vacancy.is_published = False
        self.vacancy.save()
        
        response = self.client.get(reverse('vacancy_detail', args=[self.vacancy.id]))
        self.assertEqual(response.status_code, 404)

    def test_application_model_methods(self):
        """Test Application model methods"""
        application = Application.objects.create(
            vacancy=self.vacancy,
            name='Test User',
            email='test@example.com',
            phone='+998901234567',
            cover_letter='Test cover letter',
            answers={
                str(self.field1.id): 'Test experience',
                str(self.field2.id): 'Test skills'
            }
        )
        
        self.assertEqual(str(application), 'Test User - Test Vacancy')
        self.assertTrue(hasattr(application, 'created_at'))
        self.assertEqual(application.answers[str(self.field1.id)], 'Test experience')
