```mermaid
erDiagram
    User {
        int id PK
        string role
        string first_name
        string last_name
        string email UK
        string phone
        bool is_admin
        bool is_superuser
        bool is_active
        bool is_staff
        int community_id FK
        datetime created_at
        datetime updated_at
    }

    EmailVerificationToken {
        int id PK
        int user_id FK, UK
        uuid token UK
        datetime created_at
    }

    PasswordResetToken {
        int id PK
        int user_id FK
        uuid token UK
        datetime created_at
        bool is_used
    }

    Community {
        int id PK
        string name
        string city
        string address
        bool applications_open
        datetime created_at
        datetime updated_at
    }

    CommunityAdminApplication {
        int id PK
        int applicant_id FK
        int community_id FK
        string status
        datetime applied_at
        datetime reviewed_at
        int reviewed_by_id FK
    }

    Announcement {
        int id PK
        string title
        text content
        string urgency
        datetime created_at
        datetime updated_at
    }

    Business {
        int id PK
        string name
        string category
        int owner_id FK
        int community_id FK
        string status
        text rejection_reason
        datetime created_at
    }

    BusinessBranch {
        int id PK
        int business_id FK
        int community_id FK
        string address
        string city
        string contact_phone
        string contact_email
        string status
        text rejection_reason
        datetime created_at
    }

    BusinessOwnerHistory {
        int id PK
        int business_id FK
        int owner_id FK
        datetime transferred_at
    }

    BusinessRating {
        int id PK
        int business_id FK
        int user_id FK
        int stars
        datetime created_at
        datetime updated_at
    }

    Follow {
        int id PK
        int follower_id FK
        int business_id FK
        datetime created_at
    }

    Post {
        int id PK
        int author_id FK
        int branch_id FK
        int community_id FK
        string post_type
        text content
        string status
        text takedown_reason
        datetime created_at
        datetime updated_at
    }

    PostMedia {
        int id PK
        int post_id FK
        file file
        string media_type
        int file_size
        float duration
        datetime created_at
    }

    Like {
        int id PK
        int user_id FK
        int post_id FK
        datetime created_at
    }

    Comment {
        int id PK
        int author_id FK
        int post_id FK
        int parent_id FK
        text content
        text takedown_reason
        bool is_active
        datetime created_at
    }

    CommentLike {
        int id PK
        int user_id FK
        int comment_id FK
        datetime created_at
    }

    Report {
        int id PK
        int reporter_id FK
        int post_id FK
        int comment_id FK
        string reason
        bool is_reviewed
        datetime reviewed_at
        datetime created_at
    }

    Notification {
        int id PK
        int recipient_id FK
        int actor_id FK
        string notification_type
        string message
        int post_id FK
        int comment_id FK
        int business_id FK
        int announcement_id FK
        int actor_count
        bool is_read
        datetime created_at
        datetime updated_at
    }

    Community ||--o{ User : "has members"
    User }o--o{ Community : "administers"
    User ||--o| EmailVerificationToken : "has verification token"
    User ||--o{ PasswordResetToken : "has reset tokens"
    User ||--o{ CommunityAdminApplication : "applies"
    Community ||--o{ CommunityAdminApplication : "receives applications"
    User ||--o{ CommunityAdminApplication : "reviews"
    Community }o--o{ Announcement : "receives"
    User ||--o{ Business : "owns"
    Community ||--o{ Business : "routes approval for"
    Business ||--o{ BusinessBranch : "has branches"
    Community ||--o{ BusinessBranch : "hosts"
    Business ||--o{ BusinessOwnerHistory : "has ownership history"
    User ||--o{ BusinessOwnerHistory : "held ownership"
    Business ||--o{ BusinessRating : "receives ratings"
    User ||--o{ BusinessRating : "rates"
    User ||--o{ Follow : "follows"
    Business ||--o{ Follow : "is followed"
    User ||--o{ Post : "authors"
    BusinessBranch ||--o{ Post : "publishes"
    Community ||--o{ Post : "contains"
    Post ||--o{ PostMedia : "has media"
    User ||--o{ Like : "likes"
    Post ||--o{ Like : "receives likes"
    User ||--o{ Comment : "writes"
    Post ||--o{ Comment : "has comments"
    Comment ||--o{ Comment : "has replies"
    User ||--o{ CommentLike : "likes"
    Comment ||--o{ CommentLike : "receives likes"
    User ||--o{ Report : "files"
    Post ||--o{ Report : "is reported by"
    Comment ||--o{ Report : "is reported by"
    User ||--o{ Notification : "receives"
    User ||--o{ Notification : "acts on"
    Post ||--o{ Notification : "relates to"
    Comment ||--o{ Notification : "relates to"
    Business ||--o{ Notification : "relates to"
    Announcement ||--o{ Notification : "relates to"
```

**Database constraints**

- `BusinessRating`: one rating per `(business, user)` pair.
- `Follow`: one follow per `(follower, business)` pair.
- `Like`: one like per `(user, post)` pair.
- `CommentLike`: one like per `(user, comment)` pair.
- `CommunityAdminApplication`: one pending application per `(applicant, community)` pair.
