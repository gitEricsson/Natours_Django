# Natours Django

Natours Django is a robust tour booking application built with Django and Docker. It provides a comprehensive backend for managing tours, bookings, user accounts, and more.

## Table of Contents

1. [🚀 Features](#-features)
2. [🛠️ Tech Stack](#️-tech-stack)
3. [📋 Prerequisites](#-prerequisites)
4. [📁 Project Structure](#-project-structure)
5. [🔧 Setup and Installation](#-setup-and-installation)
6. [🚀 Running the Application](#-running-the-application)
7. [🧪 Testing](#-testing)
8. [📄 API Documentation](#-api-documentation)
9. [📊 Database](#-database)
10. [🔑 Environment Variables](#-environment-variables)
11. [🐳 Docker Configuration](#-docker-configuration)
12. [🚀 Deployment](#-deployment)
13. [🤝 Contributing](#-contributing)
14. [📄 License](#-license)
15. [👥 Authors](#-authors)
16. [🙏 Acknowledgments](#-acknowledgments)
17. [📧 Contact](#-contact)

## 🚀 Features

- User authentication and authorization
- Tour management with geospatial features
- Booking system
- Review system
- Appointment scheduling
- Social authentication
- Email notifications (using Brevo)
- API documentation with Swagger

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL with PostGIS extension, RDS
- **Containerization**: Docker
- **Caching**: Redis
- **Task Queue**: Celery
- **Reverse Proxy**: Nginx
- **Cloud Platform**: AWS (ECR & EC2)
- **Continous Integration/Continous Deployment(CI/CD)**: CircleCI
- **Authentication**: JWT

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL with PostGIS
- GDAL library
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Domain name (optional, but recommended for production)

## 📁 Project Structure

```
natours_django/
├── appointments/       # Tour appointment management
├── bookings/           # Booking logic and models
├── dev-data/           # Development data and loaders
├── reviews/            # Tour review system
├── social_auth/        # Social authentication
├── tours/              # Tour management and geospatial features
├── users/              # User management
├── Natours_Django/     # Main project settings
├── nginx/              # Nginx configuration for production
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker configuration for development
├── Dockerfile.prod     # Docker configuration for production
├── requirements.txt    # Python dependencies
└── manage.py           # Django management script
```

## 🔧 Setup and Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-username/natours-django.git
   cd natours-django
   ```

2. Create environment files:

   Create `.env`:

   ```
   SECRET_KEY=your_secret_key
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   SQL_ENGINE=django.contrib.gis.db.backends.postgis
   SQL_DATABASE=natours_dev
   SQL_USER=natours_user
   SQL_PASSWORD=natours_password
   SQL_HOST=db
   SQL_PORT=5432
   DATABASE=postgres
   DJANGO_INITIALIZE_DATA=true
   ```

   Create `.env.db`:

   ```
   POSTGRES_USER=natours_user
   POSTGRES_PASSWORD=natours_password
   POSTGRES_DB=natours_dev
   ```

3. Build and run with Docker:

   ```
   docker-compose up --build
   ```

4. Initialize the database (first time only):
   ```
   docker-compose exec web python manage.py migrate
   docker-compose exec web python dev-data/data/data_loader.py --import
   docker-compose exec web python dev-data/data/data_loader.py --importDates
   ```

## 🚀 Running the Application

1. Set up AWS RDS with PostGIS:

   - Create PostgreSQL instance
   - Enable PostGIS extension
   - Configure security groups

2. Update environment variables for production:

   - Set DEBUG=0
   - Update DATABASE_URL with RDS credentials
   - Configure allowed hosts

3. Deploy using Docker:

   - For development:

   ```
   docker-compose -f docker-compose.dev.yml up --build
   ```

   - For production:

   ```
   docker-compose -f docker-compose.prod.yml up --build
   ```

4. Access development server:
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

The application will be available at `http://localhost:8000` for development and `http://localhost:80` for production.

## 🧪 Testing

Run tests using:

```bash
docker-compose exec web python manage.py test
```

## 📄 API Documentation

API documentation is available using Swagger. After running the application, visit:

```
http://localhost:8000/swagger/
```

## 📊 Database

The project uses PostgreSQL with PostGIS extension for geospatial features. The database configuration can be found in the `DATABASES` setting in `settings.py`:

```133:142:Natours_Django/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('SQL_DATABASE', 'Natours_Django'),
        'USER': os.environ.get('SQL_USER', 'postgres'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', ''),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}
```

## 🔑 Environment Variables

Key environment variables are stored in the `.env` and `.env.db` files. Make sure to keep these files secure and never commit them to version control.

## 🐳 Docker Configuration

The project includes separate Dockerfiles for development and production:

- `Dockerfile`: Development configuration
- `Dockerfile.prod`: Production configuration

Docker Compose files:

- `docker-compose.dev.yml`: Development setup
- `docker-compose.prod.yml`: Production setup

## 🚀 Deployment

For AWS production deployment:

1. Update the `DJANGO_ALLOWED_HOSTS` in your `.env` file with your domain.

2. Build the Docker images:

   ```bash
   docker-compose -f docker-compose.staging.yml build
   ```

3. Log in to AWS ECR repository:

   ```bash
   aws ecr get-login-password --region <aws-region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com
   ```

4. Tag and Push images to ECR:

   ```bash
   docker tag natours-django_web:latest <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/natours-django:web
   docker tag natours-django_nginx:latest <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/natours-django:nginx
   docker push <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/natours-django:web
   docker push <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/natours-django:nginx
   ```

5. On your EC2 instance, copy required files:

   ```bash
   scp -i /path/to/your/key.pem \
       -r $(pwd)/{app,nginx,.env.staging,.env.staging.proxy-companion,docker-compose.staging.yml} \
       ubuntu@<ec2-instance-ip>:/path/to/project
   ```

6. SSH into your EC2 instance:

   ```bash
   ssh -i /path/to/your/key.pem ubuntu@<ec2-instance-ip>
   cd /path/to/project
   ```

7. Log in to ECR and pull images:

   ```bash
   aws ecr get-login-password --region <aws-region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com
   docker pull <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/django-ec2:web
   docker pull <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/django-ec2:nginx-proxy
   ```

8. Run the containers:
   ```bash
   docker-compose -f docker-compose.staging.yml up -d
   ```

Note: When first accessing your domain, you may see a certificate security warning. This is expected if using a staging certificate. Click "Advanced" and then "Proceed" to access your application.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Ericsson Raphael - Initial work

## 🙏 Acknowledgments

- Natours project inspiration

## 📧 Contact

For questions and support, please email: ericssonraphael@gmail.com
