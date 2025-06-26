# YAML Forge - Bitbucket YAML Parser

A Django web application with React frontend for parsing YAML files from Bitbucket repositories. This project provides a user-friendly interface to authenticate with Bitbucket, browse repositories, and parse YAML files with syntax highlighting.

## 🚀 Features

- 🔐 **Bitbucket Integration**: Authenticate using access tokens
- 📁 **Repository Management**: Browse and manage multiple repositories
- 📄 **YAML Parsing**: Parse both single and multi-document YAML files
- 🎨 **Modern UI**: Beautiful React frontend with Tailwind CSS
- 💾 **Data Persistence**: Store parsed data in Django database
- 🔍 **Real-time Parsing**: Instant parsing with loading indicators
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

- **Backend**: Django 4.2.7 with Django REST Framework
- **Frontend**: React 18 with Babel (CDN-based)
- **Styling**: Tailwind CSS
- **Database**: SQLite (configurable for production)
- **API**: RESTful API endpoints for all operations

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LuminousYuzu/yamlforge.git
   cd yamlforge
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Django migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8000`

## 🎯 Usage

### 1. Configure Repository Access

You'll need a Bitbucket access token to use this application:

1. Go to your Bitbucket account settings
2. Navigate to "App passwords" or "Access tokens"
3. Create a new token with repository read permissions
4. Copy the token for use in the application

### 2. Parse YAML Files

1. **Enter Repository Details:**
   - Workspace name (e.g., `kyleswe1`)
   - Repository name (e.g., `yaml_test`)
   - Access token

2. **Click "Parse YAML Files":**
   - The application will scan the repository for YAML files
   - Parse each file and display the results
   - Store the parsed data for future reference

3. **View Results:**
   - Browse parsed YAML data with syntax highlighting
   - View saved repositories
   - Access previously parsed files

## 📁 Project Structure

```
yamlforge/
├── yaml_parser_project/          # Django project settings
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI configuration
├── yaml_parser/                  # Django app
│   ├── models.py                 # Database models
│   ├── views.py                  # API views
│   ├── serializers.py            # DRF serializers
│   ├── bitbucket_reader.py       # Bitbucket integration
│   └── urls.py                   # App URL routing
├── templates/
│   └── index.html                # React frontend template
├── static/                       # Static files
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management script
└── README.md                     # This file
```

## 🔌 API Endpoints

- `GET /api/repositories/` - List all repositories
- `POST /api/repositories/` - Create a new repository
- `GET /api/repositories/{id}/` - Get repository details
- `POST /api/parse-repository/` - Parse YAML files from repository
- `GET /api/repositories/{id}/files/` - Get parsed files for repository
- `GET /api/yaml-files/` - List all YAML files

## 🛡️ Security Considerations

⚠️ **Important Security Notes:**

- Access tokens are stored in the database (consider encryption for production)
- The application currently uses Django's development server
- For production deployment:
  - Use environment variables for sensitive data
  - Configure proper database (PostgreSQL recommended)
  - Set up HTTPS
  - Use production-grade web server (nginx + gunicorn)
  - Implement proper authentication and authorization

## 🚀 Deployment

### Production Setup

1. **Environment Variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DEBUG=False
   export ALLOWED_HOSTS="your-domain.com"
   ```

2. **Database Configuration:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'yamlforge',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Static Files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Web Server:**
   - Use nginx as reverse proxy
   - Use gunicorn as WSGI server
   - Configure SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django team for the excellent web framework
- React team for the powerful frontend library
- Tailwind CSS for the utility-first CSS framework
- PyYAML for YAML parsing capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/LuminousYuzu/yamlforge/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

**Happy YAML Parsing! 🎉** 