# TezXizmat

REST API backend for a service marketplace platform — connecting customers with service providers, with order management, reviews, real-time chat, and staff administration.

## Features

- **Customer Management** — registration, profiles, and authentication
- **Email OTP Verification** — secure signup/login via one-time passcodes
- **Orders** — create, track, and manage service orders
- **Reviews & Ratings** — customer feedback on completed services
- **Chat** — messaging between customers and service staff
- **Staff Panel** — dedicated endpoints and permissions for staff/service providers
- **JWT Authentication** — secure token-based auth with refresh tokens
- **Password Reset** — email-based password recovery flow
- **API Documentation** — auto-generated Swagger/OpenAPI docs (drf-yasg)

## Tech Stack

- **Framework:** Django 4.2, Django REST Framework 3.14
- **Database:** PostgreSQL (via `psycopg2-binary`)
- **Auth:** `djangorestframework-simplejwt` (JWT), `django-rest-passwordreset`
- **API Docs:** `drf-yasg` (Swagger / ReDoc)
- **CORS:** `django-cors-headers`
- **Media/Images:** Pillow
- **Config:** `python-decouple` (environment-based settings)

## Project Structure

```
TezXizmat/
├── config/              # Project settings, URLs, WSGI/ASGI
├── customer/            # Customer accounts & profiles
├── staff/               # Staff/service provider management
├── orders/              # Order creation & tracking
├── reviews/             # Ratings and reviews
├── chat/                # Messaging between customers and staff
├── email_otp/           # OTP-based email verification
├── templates/emails/    # Email templates (OTP, password reset, etc.)
├── manage.py
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Zarnigor/TezXizmat.git
   cd TezXizmat
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables

   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_NAME=tezxizmat_db
   DATABASE_USER=postgres
   DATABASE_PASSWORD=your-password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. Apply migrations
   ```bash
   python manage.py migrate
   ```

5. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server
   ```bash
   python manage.py runserver
   ```

   API available at `http://localhost:8000`

## API Documentation

Once running, interactive API docs are available at:

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Authentication

The API uses JWT authentication. After login, include the access token in requests:

```
Authorization: Bearer <access_token>
```

Tokens can be refreshed via the token refresh endpoint once it expires.

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m "Add your feature"`
3. Push to the branch: `git push origin feature/your-feature`
4. Open a pull request

## License

Proprietary — All rights reserved.

## Contact

**Developer:** Zarnigor
**Email:** mercurial1255@gmail.com
