# Hotel Management System

A Django-based hotel management project for exploring room discovery, guest accounts, wishlist-based reservations, and booking history.

## Project features

- Browse room categories and room details
- Check room availability by dates
- Add rooms and optional services to a wishlist
- Submit reservation requests from selected wishlist items
- Guest registration, login, and profile management
- View reservation history
- Django admin for administrative management

## Tech stack

- **Backend:** Python, Django
- **Frontend:** Django templates, HTML, CSS, JavaScript, Bootstrap
- **Database:** SQLite (default local setup)

## Run the Django app locally

> Django is not executable on GitHub Pages. Pages hosts the static showcase only. To run the interactive backend features, start Django locally.

1. Clone this repository and enter the project folder.
2. Create and activate a Python virtual environment.
3. Install dependencies from `requirements.txt` (if present) or install Django and the packages listed in the project.
4. Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## GitHub Pages

A static project showcase is published from the `docs/` directory through GitHub Actions. It showcases the hotel concept and room categories.

**The GitHub Pages site does not provide live booking, login, availability checks, checkout, or database access.** Those features require the Django backend.

## Project structure

- `hotel_managemen_system/`: Django project configuration
- `hotel_room/`: room model, catalog, availability endpoints
- `room_booking/`: wishlist and booking logic
- `user_profile/`: guest accounts and profiles
- `templates/`: server-rendered Django pages
- `static/`: CSS and image assets
- `docs/`: GitHub Pages static showcase
