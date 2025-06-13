from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async
from ..models import User, AboutSection, Vacancy, Feedback
from ..keyboards.keyboards import (
    get_language_keyboard,
    get_contact_keyboard,
    get_gender_keyboard,
    get_main_menu_keyboard,
    get_feedback_keyboard,
    get_vacancy_details_button,
    get_profile_edit_keyboard,
)
from ..texts import TEXTS
import logging

# Define conversation states
(
    LANGUAGE,        # 0
    CONTACT,         # 1
    NAME,           # 2
    LASTNAME,       # 3
    GENDER,         # 4
    BIRTHDAY,       # 5
    LOCATION,       # 6
    MAIN_MENU,      # 7
    FEEDBACK_MENU,  # 8
    AWAITING_FEEDBACK, # 9
    EDIT_PROFILE,   # 10
    EDIT_NAME,      # 11
    EDIT_LASTNAME,  # 12
    EDIT_PHONE,     # 13
    EDIT_LOCATION,  # 14
) = range(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "👋 Welcome / Xush kelibsiz / Добро пожаловать!",
        reply_markup=get_language_keyboard()
    )
    return LANGUAGE

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    language = query.data.split('_')[1]
    old_language = context.user_data.get('language')
    context.user_data['language'] = language
    
    text_dict = TEXTS[language]
    
    # Check if user is already registered
    try:
        user = await get_user_by_tg_id(query.from_user.id)
        if user:
            # Update user language
            user.language = language
            await sync_to_async(user.save)()
            
            await query.message.reply_text(
                text_dict['language_changed'],
                reply_markup=get_main_menu_keyboard(text_dict)
            )
            return MAIN_MENU
    except User.DoesNotExist:
        pass
    
    # If not registered, continue with registration
    await query.message.reply_text(text_dict['language_selected'])
    await query.message.reply_text(
        text_dict['contact_required'],
        reply_markup=get_contact_keyboard(text_dict)
    )
    return CONTACT

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contact"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    contact = update.message.contact
    context.user_data['phone'] = contact.phone_number
    
    await update.message.reply_text(text_dict['enter_name'])
    return NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    name = update.message.text
    context.user_data['name'] = name
    
    await update.message.reply_text(text_dict['enter_lastname'])
    return LASTNAME

async def handle_lastname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle lastname input"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    lastname = update.message.text
    context.user_data['lastname'] = lastname
    
    await update.message.reply_text(
        text_dict['select_gender'],
        reply_markup=get_gender_keyboard(text_dict)
    )
    return GENDER

async def gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    gender = query.data.split('_')[1]
    context.user_data['gender'] = gender
    
    await query.message.reply_text(text_dict['enter_birthday'])
    return BIRTHDAY

async def handle_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle birthday input"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    try:
        # Parse and validate the date
        birthday = datetime.strptime(update.message.text, '%d.%m.%Y').date()
        
        # Store the date object directly
        context.user_data['birthday'] = birthday
        
        # Debug logging
        logging.info(f"Birthday saved: {birthday}")
        logging.info(f"Current user data: {context.user_data}")
        
        await update.message.reply_text(text_dict['enter_location'])
        return LOCATION
        
    except ValueError as e:
        logging.error(f"Birthday parsing error: {str(e)}")
        await update.message.reply_text(text_dict['invalid_birthday'])
        return BIRTHDAY

@sync_to_async
def create_or_update_user(tg_id, user_data):
    """Create or update user in database"""
    return User.objects.update_or_create(
        tg_id=tg_id,
        defaults={
            'name': user_data['name'],
            'lastname': user_data['lastname'],
            'gender': user_data['gender'],
            'birthday': user_data['birthday'],
            'location': user_data['location'],
            'phone': user_data['phone'],
            'language': user_data['language']
        }
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location input and complete registration"""
    try:
        language = context.user_data.get('language', 'uz')
        text_dict = TEXTS[language]
        
        # Debug logging
        logging.info(f"User data before location save: {context.user_data}")
        
        # Verify all required data is present
        required_fields = ['name', 'lastname', 'gender', 'birthday', 'phone', 'language']
        missing_fields = [field for field in required_fields if field not in context.user_data]
        
        if missing_fields:
            logging.error(f"Missing required fields: {missing_fields}")
            await update.message.reply_text(
                text_dict['error_message']
            )
            return LOCATION
        
        location = update.message.text
        user_data = context.user_data.copy()
        user_data['location'] = location
        
        # Create or update user using sync_to_async wrapper
        try:
            user, created = await create_or_update_user(
                update.message.from_user.id,
                user_data
            )
            logging.info(f"User {'created' if created else 'updated'} successfully")
            
            await update.message.reply_text(
                text_dict['welcome'],
                reply_markup=get_main_menu_keyboard(text_dict)
            )
            return MAIN_MENU
            
        except Exception as e:
            logging.error(f"Database error while saving user: {str(e)}")
            await update.message.reply_text(
                text_dict['error_message']
            )
            return LOCATION
            
    except Exception as e:
        logging.error(f"Error in handle_location: {str(e)}")
        try:
            await update.message.reply_text(
                text_dict['error_message']
            )
        except:
            await update.message.reply_text(
                "Xatolik yuz berdi. Iltimos, /start buyrug'ini yuborib, qaytadan urinib ko'ring."
            )
        return LOCATION

@sync_to_async
def get_about_section():
    return AboutSection.objects.first()

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about section"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    about = await get_about_section()
    if about:
        text_field = 'text_uz' if language == 'uz' else 'text_ru'
        await update.message.reply_photo(
            photo=about.image,
            caption=getattr(about, text_field)
        )
    else:
        await update.message.reply_text("Information not available")
    return MAIN_MENU

@sync_to_async
def get_vacancies():
    return list(Vacancy.objects.filter(is_published=True))

async def show_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available vacancies"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    # Ensure we have the user's Telegram ID in the user_data
    if update.message and update.message.from_user:
        context.user_data['tg_id'] = update.message.from_user.id
    
    # Debug log to see what data we have
    logging.info(f"User data being passed: {context.user_data}")
    
    vacancies = await get_vacancies()
    if not vacancies:
        await update.message.reply_text(text_dict['no_vacancies'])
        return MAIN_MENU
    
    for vacancy in vacancies:
        text_field = 'short_text_uz' if language == 'uz' else 'short_text_ru'
        await update.message.reply_photo(
            photo=vacancy.image,
            caption=getattr(vacancy, text_field),
            reply_markup=get_vacancy_details_button(vacancy.id, text_dict, context.user_data)
        )
    return MAIN_MENU

async def show_feedback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show feedback menu"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    await update.message.reply_text(
        text_dict['feedback'],
        reply_markup=get_feedback_keyboard(text_dict)
    )
    return FEEDBACK_MENU

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback submission"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    if update.message.text in [text_dict['complaint'], text_dict['suggestion']]:
        feedback_type = 'complaint' if update.message.text == text_dict['complaint'] else 'suggestion'
        context.user_data['feedback_type'] = feedback_type
        await update.message.reply_text(text_dict['enter_feedback'])
        return AWAITING_FEEDBACK
    elif update.message.text == text_dict['back']:
        await update.message.reply_text(
            text_dict['menu'],
            reply_markup=get_main_menu_keyboard(text_dict)
        )
        return MAIN_MENU
    return FEEDBACK_MENU

@sync_to_async
def get_user_by_tg_id(tg_id):
    return User.objects.get(tg_id=tg_id)

@sync_to_async
def create_feedback(user, feedback_type, message):
    return Feedback.objects.create(
        user=user,
        type=feedback_type,
        message=message
    )

async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save feedback to database"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    user = await get_user_by_tg_id(update.message.from_user.id)
    await create_feedback(
        user=user,
        feedback_type=context.user_data['feedback_type'],
        message=update.message.text
    )
    
    await update.message.reply_text(
        text_dict['feedback_sent'],
        reply_markup=get_main_menu_keyboard(text_dict)
    )
    return MAIN_MENU

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile with edit options"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    try:
        user = await get_user_by_tg_id(update.message.from_user.id)
        gender_text = text_dict['male'] if user.gender == 'male' else text_dict['female']
        
        profile_text = text_dict['profile_info'].format(
            name=user.name,
            lastname=user.lastname,
            phone=user.phone,
            gender=gender_text,
            birthday=user.birthday.strftime('%d.%m.%Y'),
            location=user.location
        )
        
        logging.info("Showing profile and edit options")
        reply_markup = get_profile_edit_keyboard(text_dict)
        
        await update.message.reply_text(profile_text, reply_markup=reply_markup)
        logging.info("Transitioning to EDIT_PROFILE state")
        return EDIT_PROFILE
        
    except Exception as e:
        logging.error(f"Error showing profile: {str(e)}")
        await update.message.reply_text(text_dict['error_message'])
        return MAIN_MENU

async def handle_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile edit menu selection"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    text = update.message.text
    
    logging.info(f"Profile edit handler called with text: {text}")
    
    if text == text_dict['back']:
        logging.info("Back button pressed, returning to main menu")
        await update.message.reply_text(
            text_dict['menu'],
            reply_markup=get_main_menu_keyboard(text_dict)
        )
        return MAIN_MENU
    
    edit_states = {
        text_dict['edit_name']: (EDIT_NAME, 'enter_name'),
        text_dict['edit_lastname']: (EDIT_LASTNAME, 'enter_lastname'),
        text_dict['edit_phone']: (EDIT_PHONE, 'enter_phone'),
        text_dict['edit_location']: (EDIT_LOCATION, 'enter_location'),
    }
    
    if text in edit_states:
        state, prompt_key = edit_states[text]
        context.user_data['editing_field'] = text
        logging.info(f"Selected edit option: {text}, moving to state: {state}")
        await update.message.reply_text(text_dict[prompt_key])
        return state
    
    logging.warning(f"Unrecognized edit option: {text}")
    return EDIT_PROFILE

async def handle_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile field edit"""
    language = context.user_data.get('language', 'uz')
    text_dict = TEXTS[language]
    
    try:
        user = await get_user_by_tg_id(update.message.from_user.id)
        field = context.user_data.get('editing_field')
        new_value = update.message.text
        
        logging.info(f"Handling edit for field: {field} with new value: {new_value}")
        
        field_mapping = {
            text_dict['edit_name']: 'name',
            text_dict['edit_lastname']: 'lastname',
            text_dict['edit_phone']: 'phone',
            text_dict['edit_location']: 'location',
        }
        
        if field in field_mapping:
            db_field = field_mapping[field]
            logging.info(f"Updating user field: {db_field} = {new_value}")
            setattr(user, db_field, new_value)
            await sync_to_async(user.save)()
            
            await update.message.reply_text(
                text_dict['update_success'],
                reply_markup=get_main_menu_keyboard(text_dict)
            )
            return await show_profile(update, context)
        else:
            logging.error(f"Unknown field to edit: {field}")
            
    except Exception as e:
        logging.error(f"Error updating profile: {str(e)}")
        await update.message.reply_text(text_dict['error_message'])
    
    return EDIT_PROFILE

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change user language"""
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык",
        reply_markup=get_language_keyboard()
    )
    return LANGUAGE 