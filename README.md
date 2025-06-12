# IMARKETING Telegram Bot & Website

A Django-based system that includes a Telegram bot for user interaction and a website for vacancy listings.

## Features

### Telegram Bot
- Multi-language support (Uzbek/Russian)
- User registration with profile management
- Company information viewing
- Vacancy browsing
- Feedback submission system

### Website
- Public vacancy listings
- Detailed vacancy views
- Job application system
- Language switching (Uzbek/Russian)

### Admin Panel
- User management
- Vacancy management
- Feedback monitoring
- Application tracking
- About section customization

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd imarketing_django_bot
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the project root:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. In a separate terminal, run the Telegram bot:
```bash
python manage.py runbot
```

## Usage

### Admin Panel
1. Access the admin panel at `http://localhost:8000/admin/`
2. Log in with superuser credentials
3. Manage users, vacancies, feedback, and applications

### Website
- Access the public website at `http://localhost:8000/`
- Browse vacancies and submit applications

### Telegram Bot
1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. Follow the registration process
4. Use the main menu to access features

## Project Structure

```
imarketing_django_bot/
├── bot/                    # Telegram bot app
│   ├── management/        # Bot management commands
│   ├── handlers/         # Bot message handlers
│   └── keyboards/        # Bot keyboard layouts
├── website/               # Website app
│   ├── templates/        # Website templates
│   └── static/           # Static files
├── templates/             # Global templates
├── media/                # User-uploaded files
└── imarketing/           # Project settings
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 