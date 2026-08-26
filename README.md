# CommunalSpace

A social and civic backend for neighborhood communities — built with Django REST Framework. Residents join a community, follow a local social feed, discover and rate businesses, and receive official announcements from community admins. Long-term, Communal Space is aimed at becoming a smart-community operating system, extending into incident reporting and security integrations.

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Auth:** JWT via `djangorestframework-simplejwt` (login, logout with blacklisting, refresh with rotation, password change/reset, email verification)
- **Database:** SQLite (development), PostgreSQL (production target)
- **Config:** `python-decouple` for environment variables
- **Testing:** `pytest-django`
- **API Docs:** `drf-spectacular` (installed, not yet configured)
- **CI:** GitHub Actions running the test suite on every push
- **Tooling:** pre-commit hooks, `django-extensions`, `django-filter`, `whitenoise`

## Apps

### `accounts`

Identity and access control.

- Registration, login, logout, JWT refresh
- Email verification (24hr token expiry)
- Password change and reset (20min token expiry for reset)
- Role-based system: **resident → business owner** (on business approval) → **community admin** (via application) → **platform admin** (via `createsuperuser`)
- Custom permission classes: `IsAdmin`, `IsSelfOrAdmin`, `IsCommunityAdminOrAdmin`, `IsCommunityAdmin`, `IsBusinessOwnerOrAdmin`

### `communities`

Community structure and membership.

- Communities support multiple admins (many-to-many, not a single FK)
- Users belong to exactly one community at a time — join/leave
- Community admin application system: platform admin opens/closes an application season, residents apply, platform admin approves or rejects
- Approval upgrades a user's role and adds them to the community's admin set

### `businesses`

The business directory.

- Business registration requires a first branch in the same request; the `Business` model is the "face," `BusinessBranch` holds branch-specific detail (address, city, contact info)
- Community admin reviews and approves/rejects a business (with a reason) — approval simultaneously approves the first branch and upgrades the owner's role
- Subsequent branches go through their own independent per-community approval
- Ownership history tracked automatically
- Star ratings: any user can rate an approved business 0.5–5.0 stars in half-star steps (stored internally as an integer 1–10); rating again updates your existing score rather than duplicating it; `average_rating` and `rating_count` are computed live on list/detail responses, never stored

### `posts`

The community social feed.

- Posts are either **user posts** (belong to the author's current community) or **business posts** (belong to the community of an approved branch the poster owns)
- Up to 4 media items per post (image, video, GIF) with automatic type detection
- Cursor-paginated feed, filterable by community and post type — not restricted to the viewer's own community
- Likes, comments with nested replies, and comment likes
- Reactive moderation: any user can report a post or comment; a community admin (scoped to their own community) or platform admin reviews the report and either dismisses it or removes the content (soft delete — `Post.status` / `Comment.is_active`, both with a required takedown reason)

### `announcements`

Official broadcasts from admins, distinct from the peer-to-peer post feed.

- Only community admins or platform admins can create an announcement
- A single announcement can target multiple communities at once — a community admin can only target communities they actually administer
- Three urgency levels: info, warning, critical
- Open to all authenticated users to read, regardless of their own community, so residents can see notices from communities they don't belong to
- Full CRUD, with community-admin edit/delete scoping enforced against *every* community an announcement targets, not just one

## Setup

```bash
git clone <repo-url>
cd communalspace
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example` if present) with at minimum:

```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-gmail-address
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

Then:

```bash
python manage.py migrate
python manage.py createsuperuser   # creates a platform admin
python manage.py runserver
```

## Running Tests

```bash
pytest
```

Each app has its own test suite covering CRUD, authorization/role scoping, side effects (e.g. role upgrades on approval, cascading branch approval), and invalid-input handling.

## What's Next

- **API documentation** — configure `drf-spectacular` for a live schema/Swagger UI (already installed)
- **Business discovery filtering** — category, city, and community filters on the business directory (category doesn't exist as a field yet; city currently lives on `BusinessBranch`, not `Business`)
- **Notifications system** — business approval status, new posts/likes/comments, announcement broadcasts, report outcomes
- **Direct messaging** — resident-to-resident and resident-to-business-owner
- **Production readiness** — switch from SQLite to PostgreSQL, move media storage from local disk to AWS S3 via `django-storages`, point email verification/reset links at frontend URLs instead of localhost

### Long-Term Vision

Communal Space's longer-term direction is a "civic OS" for neighborhoods — incident and suspicious-activity reporting, real-time notifications over WebSockets, and eventual integration with security hardware (cameras, sensors) layered on top of the community structure already in place.
