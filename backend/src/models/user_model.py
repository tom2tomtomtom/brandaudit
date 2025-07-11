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
    reports = db.relationship(
        "Report", backref="user", lazy=True, cascade="all, delete-orphan"
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


class Brand(db.Model):
    """Brand model for storing brand information"""

    __tablename__ = "brands"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Brand information
    name = db.Column(db.String(200), nullable=False, index=True)
    website = db.Column(db.String(500), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Brand metadata
    logo_url = db.Column(db.String(500), nullable=True)
    primary_color = db.Column(db.String(7), nullable=True)  # Hex color
    founded_year = db.Column(db.Integer, nullable=True)
    headquarters = db.Column(db.String(200), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    analyses = db.relationship("Analysis", backref="brand", lazy=True)

    def __repr__(self):
        return f"<Brand {self.name}>"

    def to_dict(self):
        """Convert brand to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "website": self.website,
            "industry": self.industry,
            "description": self.description,
            "logo_url": self.logo_url,
            "primary_color": self.primary_color,
            "founded_year": self.founded_year,
            "headquarters": self.headquarters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Analysis(db.Model):
    """Analysis model for storing brand audit results"""

    __tablename__ = "analyses"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)  # Allow anonymous analyses
    brand_id = db.Column(db.String(36), db.ForeignKey("brands.id"), nullable=False)

    # Analysis data
    brand_name = db.Column(db.String(200), nullable=False)  # Keep for backward compatibility
    analysis_types = db.Column(db.JSON, nullable=True)  # List of analysis types requested
    status = db.Column(
        db.String(20), default="started", nullable=False
    )  # started, processing, completed, failed
    progress = db.Column(db.Integer, default=0)

    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    status_message = db.Column(db.String(200), nullable=True)  # Current processing step

    # Analysis results - stored as JSON
    results = db.Column(db.JSON, nullable=True)

    # Analysis metadata
    analysis_version = db.Column(db.String(20), default="1.0", nullable=False)
    data_sources = db.Column(db.JSON, nullable=True)  # Track which data sources were used

    # Performance metrics
    processing_time_seconds = db.Column(db.Float, nullable=True)
    concurrent_processing_used = db.Column(db.Boolean, default=False)
    cache_hit_rate = db.Column(db.Float, nullable=True)  # Percentage of cache hits

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    reports = db.relationship("Report", backref="analysis", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis {self.id} - {self.brand_name}>"

    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "brand_id": self.brand_id,
            "brand_name": self.brand_name,
            "analysis_types": self.analysis_types,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "results": self.results,
            "analysis_version": self.analysis_version,
            "data_sources": self.data_sources,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def update_status(self, status, error_message=None, progress=None):
        """Update analysis status"""
        self.status = status
        if error_message:
            self.error_message = error_message
        if progress is not None:
            self.progress = progress
        if status == "completed":
            self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_results(self, results):
        """Update analysis results"""
        self.results = results
        self.updated_at = datetime.utcnow()
        db.session.commit()


class Report(db.Model):
    """Report model for storing generated reports"""

    __tablename__ = "reports"

    # Primary key
    id = db.Column(db.String(36), primary_key=True)  # UUID

    # Foreign keys
    analysis_id = db.Column(db.String(36), db.ForeignKey("analyses.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)

    # Report information
    report_type = db.Column(db.String(50), nullable=False)  # pdf, powerpoint, markdown
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)

    # Report metadata
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    pages_count = db.Column(db.Integer, nullable=True)

    # Generation status
    status = db.Column(db.String(20), default="generating", nullable=False)  # generating, completed, failed
    error_message = db.Column(db.Text, nullable=True)

    # Download tracking
    download_count = db.Column(db.Integer, default=0, nullable=False)
    last_downloaded = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Report {self.id} - {self.filename}>"

    def to_dict(self):
        """Convert report to dictionary"""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "user_id": self.user_id,
            "report_type": self.report_type,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "title": self.title,
            "description": self.description,
            "pages_count": self.pages_count,
            "status": self.status,
            "error_message": self.error_message,
            "download_count": self.download_count,
            "last_downloaded": self.last_downloaded.isoformat() if self.last_downloaded else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
        self.last_downloaded = datetime.utcnow()
        db.session.commit()

    def update_status(self, status, error_message=None):
        """Update report status"""
        self.status = status
        if error_message:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()
        db.session.commit()


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
