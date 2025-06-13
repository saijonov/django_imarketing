from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import datetime
import tempfile
import shutil
from .models import User, Vacancy, VacancyField, Feedback, AboutSection
from .handlers.base import (
    start,
    language_callback,
    contact_handler,
    handle_name,
    handle_lastname,
    gender_callback,
    handle_birthday,
    handle_location,
)
from telegram import Update, Chat, Message, User as TelegramUser
from telegram.ext import CallbackContext, ConversationHandler
from unittest.mock import Mock, AsyncMock, patch
import json

# Create a temp media root for test files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BotModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image = SimpleUploadedFile('test_image.gif', self.image_content, content_type='image/gif')
        
        # Create test user
        self.user = User.objects.create(
            tg_id=123456789,
            name='Test User',
            lastname='Test Lastname',
            gender='male',
            birthday='1990-01-01',
            location='Test City',
            phone='+998901234567',
            language='uz'
        )
        
        # Create test vacancy
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            short_text_uz='Test short UZ',
            short_text_ru='Test short RU',
            full_text_uz='Test full UZ',
            full_text_ru='Test full RU',
            image=self.image,
            is_published=True
        )

    def tearDown(self):
        """Clean up test files"""
        try:
            shutil.rmtree(TEMP_MEDIA_ROOT)
        except Exception as e:
            print(f'Error while deleting temp directory: {e}')

    def test_user_model(self):
        """Test User model"""
        self.assertEqual(str(self.user), 'Test User Test Lastname')
        self.assertTrue(hasattr(self.user, 'created_at'))
        self.assertEqual(self.user.language, 'uz')

    def test_vacancy_model(self):
        """Test Vacancy model"""
        self.assertEqual(str(self.vacancy), 'Test Vacancy')
        self.assertTrue(self.vacancy.is_published)
        
        # Test custom fields
        field = VacancyField.objects.create(
            vacancy=self.vacancy,
            name='experience',
            label_uz='Tajriba',
            label_ru='Опыт',
            field_type='text',
            required=True,
            order=1
        )
        self.assertEqual(str(field), 'Test Vacancy - experience')

    def test_feedback_model(self):
        """Test Feedback model"""
        feedback = Feedback.objects.create(
            user=self.user,
            type='complaint',
            message='Test feedback'
        )
        self.assertEqual(str(feedback), 'Test User - complaint')
        self.assertTrue(hasattr(feedback, 'created_at'))

    def test_about_section_model(self):
        """Test AboutSection model"""
        about = AboutSection.objects.create(
            text_uz='Test about UZ',
            text_ru='Test about RU',
            image=self.image
        )
        self.assertEqual(str(about), 'About Section')
        self.assertTrue(hasattr(about, 'updated_at'))

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BotHandlerTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.chat = Chat(id=1, type='private')
        self.telegram_user = TelegramUser(
            id=123456789,
            is_bot=False,
            first_name='Test',
            last_name='User'
        )

    async def test_start_handler(self):
        """Test start command handler"""
        update = AsyncMock(spec=Update)
        update.message = AsyncMock()
        update.message.chat = self.chat
        update.message.from_user = self.telegram_user
        update.message.reply_text = AsyncMock()
        
        context = AsyncMock(spec=CallbackContext)
        context.user_data = {}
        
        state = await start(update, context)
        self.assertEqual(state, 0)  # LANGUAGE state
        update.message.reply_text.assert_called_once()

    async def test_language_callback(self):
        """Test language selection handler"""
        update = AsyncMock(spec=Update)
        update.callback_query = AsyncMock()
        update.callback_query.data = 'lang_uz'
        update.callback_query.from_user = self.telegram_user
        update.callback_query.message.reply_text = AsyncMock()
        
        context = AsyncMock(spec=CallbackContext)
        context.user_data = {}
        
        state = await language_callback(update, context)
        self.assertEqual(state, 1)  # CONTACT state
        self.assertEqual(context.user_data.get('language'), 'uz')
        update.callback_query.message.reply_text.assert_called()

    async def test_contact_handler(self):
        """Test contact handler"""
        update = AsyncMock(spec=Update)
        update.message = AsyncMock()
        update.message.contact = AsyncMock()
        update.message.contact.phone_number = '+998901234567'
        update.message.reply_text = AsyncMock()
        
        context = AsyncMock(spec=CallbackContext)
        context.user_data = {'language': 'uz'}
        
        state = await contact_handler(update, context)
        self.assertEqual(state, 2)  # NAME state
        self.assertEqual(context.user_data.get('phone'), '+998901234567')
        update.message.reply_text.assert_called_once()

    async def test_gender_callback(self):
        """Test gender callback handler"""
        update = AsyncMock(spec=Update)
        update.callback_query = AsyncMock()
        update.callback_query.data = 'gender_male'
        update.callback_query.message.reply_text = AsyncMock()
        update.callback_query.from_user = self.telegram_user
        
        context = AsyncMock(spec=CallbackContext)
        context.user_data = {}
        
        state = await gender_callback(update, context)
        self.assertEqual(state, 5)  # BIRTHDAY state
        self.assertEqual(context.user_data.get('gender'), 'male')
        update.callback_query.message.reply_text.assert_called_once()

    async def test_birthday_handler(self):
        """Test birthday handler"""
        update = AsyncMock(spec=Update)
        update.message = AsyncMock()
        update.message.text = '01.01.1990'
        update.message.reply_text = AsyncMock()
        update.message.from_user = self.telegram_user
        
        context = AsyncMock(spec=CallbackContext)
        context.user_data = {}
        
        state = await handle_birthday(update, context)
        self.assertEqual(state, 6)  # LOCATION state
        self.assertEqual(context.user_data.get('birthday').strftime('%d.%m.%Y'), '01.01.1990')
        update.message.reply_text.assert_called_once()
