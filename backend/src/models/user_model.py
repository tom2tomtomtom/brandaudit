"""
User model for the Brand Audit Tool
"""

from src.extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model with authentication and security features"""

    __tablename__ = "users"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile fields
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), default="user", nullable=False)  # New role field

    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login = db.Column(db.DateTime, nullable=True)

    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Relationships
    analyses = db.relationship(
        "Analysis", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()

    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()

    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
        db.session.commit()

    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        db.session.commit()

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "company": self.company,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data.update(
                {
                    "failed_login_attempts": self.failed_login_attempts,
                    "locked_until": self.locked_until.isoformat()
                    if self.locked_until
                    else None,
                }
            )

        return data


class Analysis(db.Model):
    """Analysis model for storing brand audit results"""

    __tablename__ = "analyses"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Foreign key
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # Analysis data
    company_name = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(500), nullable=True)
    status = db.Column(
        db.String(20), default="pending", nullable=False
    )  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)

    # Analysis options
    analysis_options = db.Column(db.JSON, nullable=True)

    # Results
    results = db.Column(db.JSON, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Analysis {self.id} - {self.company_name}>"

    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "website": self.website,
            "status": self.status,
            "progress": self.progress,
            "analysis_options": self.analysis_options,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }


class UploadedFile(db.Model):
    """Model for tracking uploaded files"""

    __tablename__ = "uploaded_files"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    analysis_id = db.Column(db.String(36), db.ForeignKey("analyses.id"), nullable=True)

    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)

    # File type categorization
    file_type = db.Column(
        db.String(50), nullable=False
    )  # logo, screenshot, typography, etc.

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UploadedFile {self.filename}>"

    def to_dict(self):
        """Convert file to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_type": self.file_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
