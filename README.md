# PortoTours: Django E-Commerce Booking Platform

![Django](https://img.shields.io/badge/Django-5.0+-0C4B33?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-Geospatial-2F6F4F)
![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Broker-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Async%20Tasks-37814A?logo=celery&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?logo=stripe&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Coverage](https://img.shields.io/badge/Test%20Coverage-80%25%2B-brightgreen)
[![License](https://img.shields.io/badge/License-Proprietary%20%7C%20All%20Rights%20Reserved-black.svg)](LICENSE)

> **Production-grade Django application** for multi-language tour & experience booking in Portugal with Stripe payments, real-time availability, and geospatial queries.

```text
> Note for reviewers and potential clients
>
> This repository is public as part of my portfolio. PortoTours is a production-oriented Django booking platform for tour and experience sales in Portugal, originally deployed on a DigitalOcean droplet with PostgreSQL and Redis running as separate services in the same cloud environment.
>
> Highlights:
> - End-to-end backend ownership: architecture, Django domain modeling, payments, admin workflows, and deployment.
> - Business logic depth: multi-language catalog, availability scheduling, pricing rules, booking flow, and invoice generation.
> - Production mindset: Dockerized delivery, CI/CD pipeline, S3 media storage, background jobs, and backup/recovery scripts.
>
> What to expect:
> - Mature portfolio code: this project reflects real delivery constraints and trade-offs, not a tutorial build.
> - Tested codebase: coverage was maintained at 80%+ for the main project scope.
> - Best entry points: Architecture & Tech Stack, Application Structure, Core Features, and Production Deployment.
>
> Licensing:
> - Public visibility does not grant reuse rights. See [LICENSE](LICENSE).
```

## 🎯 Project Overview

PortoTours is a comprehensive **B2C e-commerce platform** enabling customers to discover, customize, and book travel experiences (group tours and private packages) across Portugal. Built with Django, it demonstrates enterprise-grade architecture patterns including:

- **Multi-tenant booking system** with real-time calendar availability
- **Stripe payment integration** with automated invoicing and QR code tickets
- **Geospatial database queries** using PostgreSQL PostGIS extension
- **Multi-language content management** (6 supported languages: EN, ES, FR, PT-AU, PT-GB)
- **Content marketing** with destination guides, attractions, and customer testimonials
- **Cloud-native deployment** with Docker, Redis caching, and AWS S3 storage

## 🏗️ Architecture & Tech Stack

### **Backend Stack**
- **Django 5.0+** with Django REST patterns
- **PostgreSQL 14+** with PostGIS (geospatial queries)
- **Redis** (caching, Celery broker)
- **Celery** (async task processing with Beat scheduler)
- **Gunicorn** (production WSGI server)

### **Payment & Third-Party Services**
- **Stripe API** - Payment processing, customer profiles, recurring billing support
- **AWS S3** - Static files and media asset storage (images, PDFs, uploads)
- **OpenStreetMap Nominatim** - Address geocoding for meeting points
- **WeasyPrint** - PDF generation (invoices, tickets with QR codes)

### **Frontend Integration**
- Django templates with HTMX patterns
- CKEditor for rich text content management
- Bootstrap 5-based responsive design

### **Deployment Infrastructure**
- Docker containerization (Docker Hub: `kivaschenko/portotours:latest`)
- DigitalOcean VPS with separated PostgreSQL and Redis services
- Automated deployment pipeline (`deploy.sh`)

---

## 📦 Application Structure

```
portotours/
├── products/              # Core marketplace: experiences, availability calendar, pricing engine
├── purchases/             # Order management, Stripe integration, invoice generation
├── accounts/              # User authentication, profiles, email-based login
├── destinations/          # Travel guides, multi-language content, SEO optimization
├── attractions/           # Points of interest, categories, location recommendations
├── blogs/                 # Content marketing, travel guides with rich media
├── reviews/               # Customer testimonials, rating system, moderation workflow
├── home/                  # CMS landing pages, company info, navigation
├── service_layer/         # Shared utilities: S3, Stripe, emails, PDF generation
└── portotours/            # Project config, middleware, settings (dev/test/prod)
```

### **Key Models & Business Logic**

#### **Booking Domain**
- `Experience` / `ParentExperience` - Localized experience metadata with parent-child relationships
- `ExperienceEvent` - Specific tour occurrences (date, time, availability, dynamic pricing)
- `Product` - Individual customer bookings (seats or private packages)
- `ExperienceOption` - Optional add-ons (hotel pickup, upgrades)
- `ExperienceProvider` - Tour operator/vendor management

#### **Location Domain**
- `Destination` / `ParentDestination` - Content hubs linking destinations to experiences & attractions
- `Attraction` / `ParentAttraction` - Tagged POIs with recommendations
- `MeetingPoint` - Start/drop-off locations with auto-geocoding via Nominatim

#### **Transaction Domain**
- `Purchase` - Order linking User → Products → Stripe payment with full audit trail
- `Review/Testimonial` - Customer feedback moderation for homepage features

#### **User Management**
- Custom email-based authentication (not username-based)
- Extended user profiles with Stripe customer IDs and avatar uploads

---

## ✨ Core Features

✅ **Booking Engine** - Group seat reservations + private tour packages with real-time availability checking  
✅ **Pricing Optimization** - Base/child pricing, marketing discounts, per-person calculations, dynamic pricing  
✅ **Payment Processing** - Stripe integration with QR code tickets, PDF invoices, automatic email receipts  
✅ **Multi-Language SEO** - Full content in 6 languages with optimized URL structures and hreflang tags  
✅ **Smart Scheduling** - Django-Scheduler integration for calendar management and availability queries  
✅ **Geospatial Queries** - PostGIS-powered meeting point searches and destination proximity calculations  
✅ **Marketing Automation** - Hot deals flagging, scarcity indicators ("likely to sell out"), recommendation engine  
✅ **Admin Portal** - Custom Django admin with bulk operations, review moderation, performance dashboards  
✅ **Search & Discovery** - Full-text search, filtering by category/duration/time, destination browsing  
✅ **Async Task Processing** - Celery integration for email sending, PDF generation, reporting (partially implemented)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **PostgreSQL 14+** with PostGIS extension
- **Redis 6+** (for caching and Celery)
- **GDAL libraries** (for PostGIS geospatial queries)

### Development Setup

**Linux/macOS:**
```bash
# Install system dependencies
# Linux
sudo apt-get install binutils libproj-dev gdal-bin graphviz graphviz-dev

# macOS
brew install graphviz
```

**Python Environment:**
```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate

# Copy environment configuration
cp sample_env .env

# Install dependencies
pip install --upgrade pip setuptools
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Load fixture data (products, languages, attractions)
python manage.py loaddata products/fixtures/*
python manage.py loaddata products/fixtures/prod/languages.json

# Run development server
python manage.py runserver
```

Visit [http://localhost:8000/](http://localhost:8000/)

### Celery Setup (Production)
```bash
# Start worker with periodic tasks
celery -A portotours worker -l INFO --beat --scheduler django

# Optional: Monitor with Flower dashboard
celery -A portotours flower
```

### Running Tests
Historical automated test coverage for the project was maintained at **80%+** for the primary codebase.

```bash
python3 manage.py test --verbosity=2 --keepdb

# Run with coverage analysis
coverage run manage.py test
coverage report -m
```

#### Test Credentials
Load test fixtures first:
```bash
python manage.py loaddata accounts/fixtures/testing/users.json
```

| Role | Email | Password |
|------|-------|----------|
| Admin | `dev@example.com` | `112358` |
| Customer | `customer@example.com` | `$0me$eecret` |

### Static Assets & Styling

**CSS Compilation with SCSS**

The project uses `django-sass-processor` for compiling SCSS files:
- Custom styles: `static/custom_css/custom.scss`
- Framework: Bootstrap 5

```bash
# Compile SCSS and collect static files
./manage.py compilescss
./manage.py collectstatic

# Compress CSS/JS (before production deployment)
./manage.py compress
./manage.py runserver
```

Reference: [Django Sass Processor](https://github.com/jrief/django-sass-processor)

---

## 🚀 Production Deployment

### Cloud Infrastructure
- **Platform**: DigitalOcean VPS
- **Region**: Frankfurt
- **Configuration**: 2 vCPU, 4GB RAM
- **Services**: PostgreSQL 14+ and Redis 6+ (separate droplets)
- **Web Server**: Nginx with SSL/TLS certificates
- **Documentation**: [DigitalOcean Docs](https://docs.digitalocean.com/products/)

### Deployment Pipeline

#### Automated CI/CD (GitHub Actions)
```
Pull Request to main → Run tests → Build Docker image → Push to Docker Hub 
→ SSH to server → Pull new image → Deploy with zero downtime
```

**Configuration**: `.github/workflows/docker-image.yml`

The pipeline automatically:
1. Runs full test suite
2. Builds Docker image (`kivaschenko/portotours:latest`)
3. Pushes to Docker Hub
4. Connects to server via GitHub Secrets
5. Pulls new image, stops old container, launches new deployment

#### Manual Deployment

**Build and push from local machine:**
```bash
git checkout develop  # or production branch
deactivate           # exit venv if active
docker build -t kivaschenko/portotours:latest .
docker push kivaschenko/portotours:latest
```

**Deploy on server:**
```bash
ssh root@YOUR_SERVER_IP
docker pull kivaschenko/portotours:latest
docker ps -a
docker stop django-portotours
docker rm django-portotours
docker run -d --name django-portotours -p 8000:8000 \
  -e DATABASE_URL=postgres://... \
  -e REDIS_URL=redis://... \
  kivaschenko/portotours:latest
docker ps -a
systemctl reload nginx
systemctl status nginx.service
```

### Nginx Configuration
Nginx config stored in: `ssl_cert/nginx.conf`

**Exchange config with server:**
```bash
scp root@YOUR_SERVER_IP:/etc/nginx/sites-available/default ssl_cert/nginx.conf
```

**Apply changes:**
```bash
systemctl reload nginx
systemctl status nginx.service
```

### Database Backups & Recovery

**Automated Backups**: Cron job runs `backup_db.sh` to email database dumps  
**Location**: `/etc/backup_django/` on server  
**Project copies**: `cron_services/backup_db.sh` and `recovery_db.sh`

**Upload backup scripts to server:**
```bash
scp cron_services/backup_db.sh root@YOUR_SERVER_IP:/etc/backup_django/
```

**Restore from backup:**
```bash
# On server, run recovery script
/etc/backup_django/recovery_db.sh
```

---

## 🔐 Django Admin Features

### Custom Admin Interface

The application includes a sophisticated custom admin portal with:

- **Review Moderation Dashboard** - Approve/reject customer testimonials
- **Bulk Operations** - Mass update experience availability, pricing
- **Performance Dashboards** - Sales analytics, booking trends, revenue reports
- **Product Management** - Experience creation, pricing tiers, seasonal rates
- **User Management** - Customer profiles, Stripe customer sync
- **Content Management** - Destination guides, attraction tagging, blog publishing

**Access**: [http://localhost:8000/admin/](http://localhost:8000/admin/) (requires superuser)

---

## 🏆 Key Technical Achievements

### 1. **Scalable Database Design**
- Normalized data model with parent-child relationships for multi-language content
- Efficient geospatial queries using PostGIS for location-based features
- Proper indexing and query optimization for e-commerce scale

### 2. **Payment Processing**
- Full Stripe integration with webhook handling and retry logic
- Customer profile synchronization
- PCI-compliant architecture (no credit card data stored locally)
- Automated invoice generation and email delivery

### 3. **Multi-Language Architecture**
- 6 language support with URL-based language selection
- SEO-optimized content with hreflang tags
- Efficient content reuse through parent entity pattern

### 4. **Real-Time Availability**
- Calendar-based event scheduling with Django-Scheduler
- Dynamic pricing based on availability and demand
- Concurrent booking handling with proper database transactions

### 5. **Cloud Integration**
- AWS S3 storage for media assets with static file optimization
- Redis caching layer for performance
- Containerized deployment for consistency across environments

### 6. **Async Task Processing**
- Celery integration for background jobs
- Email delivery, PDF generation, data export queuing
- Beat scheduler for periodic tasks (maintenance, cleanup, reporting)

---

## 📋 Dependencies & Requirements

### Core Python Packages
```
Django==5.0.x           # Web framework
psycopg2-binary         # PostgreSQL adapter
geospatial              # PostGIS integration
stripe                  # Payment processing
celery                  # Async tasks
redis                   # Caching & broker
boto3                   # AWS S3 integration
WeasyPrint              # PDF generation
django-ckeditor         # Rich text editing
django-sass-processor   # SCSS compilation
django-scheduler        # Calendar management
requests-oauthlib       # OAuth support
```

See `requirements.txt` for complete list with pinned versions.

---

## 🤝 Development Team

**Lead Developer**: Multi-app architecture design, payment integration, deployment infrastructure  
**Contributing Developer**: Frontend participation, template development, UX implementation

---

## 📝 License

**⚠️ PROPRIETARY SOFTWARE - All Rights Reserved**

This code is proprietary and confidential. Unauthorized copying, modification, distribution, or use of this software without explicit written permission is strictly prohibited.

For licensing inquiries or permissions: Contact the repository owner.

See [LICENSE](LICENSE) for full terms.

---

## 🚀 Future Roadmap

- ✅ Full Celery async task processing implementation
- ✅ Flower monitoring dashboard
- 🔄 Advanced analytics and reporting
- 🔄 Mobile app API optimization
- 🔄 AI-powered recommendation engine
- 🔄 Multi-currency support

---

## 📞 Contact & Support

For questions about this code or consulting inquiries regarding Django e-commerce platforms, contact the repository owner.

---

**Built with ❤️ using Django, PostgreSQL, and cloud-native technologies.**
