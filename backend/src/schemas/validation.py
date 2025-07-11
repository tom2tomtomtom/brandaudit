"""
Validation schemas for the Brand Audit Tool
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re
from urllib.parse import urlparse


class BrandSearchSchema(Schema):
    """Schema for brand search requests"""

    query = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=200),
            validate.Regexp(
                r"^[a-zA-Z0-9\s\-&.,()]+$", error="Invalid characters in query"
            ),
        ],
    )


class BrandAssetsSchema(Schema):
    """Schema for brand assets requests"""

    website = fields.Url(required=True, schemes=["http", "https"])

    @validates("website")
    def validate_website(self, value):
        """Additional website validation"""
        parsed = urlparse(value)
        if not parsed.netloc:
            raise ValidationError("Invalid website URL")

        # Block localhost and private IPs for security
        if "localhost" in parsed.netloc or "127.0.0.1" in parsed.netloc:
            raise ValidationError("Localhost URLs are not allowed")


class AnalysisRequestSchema(Schema):
    """Schema for analysis requests"""

    company_name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=200),
            validate.Regexp(
                r"^[a-zA-Z0-9\s\-&.,()]+$", error="Invalid characters in company name"
            ),
        ],
    )

    website = fields.Url(required=False, allow_none=True, schemes=["http", "https"])

    analysis_options = fields.Dict(
        required=True,
        keys=fields.Str(
            validate=validate.OneOf(
                [
                    "brandPerception",
                    "competitiveAnalysis",
                    "visualConsistency",
                    "visualAnalysis",  # NEW: Enhanced visual analysis with color extraction
                    "pressCoverage",
                    "socialSentiment",
                ]
            )
        ),
        values=fields.Bool(),
    )

    uploaded_files = fields.List(
        fields.Str(), load_default=[], validate=validate.Length(max=10)
    )

    @validates("website")
    def validate_website(self, value):
        """Additional website validation"""
        if value:
            parsed = urlparse(value)
            if not parsed.netloc:
                raise ValidationError("Invalid website URL")

            # Block localhost and private IPs for security
            if "localhost" in parsed.netloc or "127.0.0.1" in parsed.netloc:
                raise ValidationError("Localhost URLs are not allowed")


class FileUploadSchema(Schema):
    """Schema for file upload validation"""

    file_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["logo", "screenshot", "typography", "brand_asset", "other"]
        ),
    )

    description = fields.Str(load_default="", validate=validate.Length(max=500))


class ReportGenerationSchema(Schema):
    """Schema for report generation requests"""

    analysis_id = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
            error="Invalid analysis ID format",
        ),
    )

    format = fields.Str(required=True, validate=validate.OneOf(["pdf", "html", "json"]))

    include_sections = fields.List(
        fields.Str(
            validate=validate.OneOf(
                ["overview", "perception", "visual", "press", "competitive"]
            )
        ),
        load_default=["overview", "perception", "visual", "press", "competitive"],
    )


class UserUpdateSchema(Schema):
    """Schema for user profile updates"""

    name = fields.Str(
        validate=[
            validate.Length(min=1, max=100),
            validate.Regexp(r"^[a-zA-Z\s\-\'\.]+$", error="Invalid characters in name"),
        ]
    )

    company = fields.Str(
        validate=[
            validate.Length(max=100),
            validate.Regexp(
                r"^[a-zA-Z0-9\s\-&.,()]+$", error="Invalid characters in company name"
            ),
        ]
    )


class PasswordChangeSchema(Schema):
    """Schema for password change requests"""

    current_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
                error="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character",
            ),
        ],
    )
    confirm_password = fields.Str(required=True)

    @validates("confirm_password")
    def validate_password_confirmation(self, value):
        """Validate password confirmation matches"""
        if "new_password" in self.context and value != self.context["new_password"]:
            raise ValidationError("Password confirmation does not match")


def validate_file_upload(file):
    """Validate uploaded file"""
    if not file:
        raise ValidationError("No file provided")

    if file.filename == "":
        raise ValidationError("No file selected")

    # Check file extension
    allowed_extensions = {"png", "jpg", "jpeg", "gif", "svg", "webp", "pdf"}
    if "." not in file.filename:
        raise ValidationError("File must have an extension")

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Check file size (16MB limit)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    max_size = 16 * 1024 * 1024  # 16MB
    if file_size > max_size:
        raise ValidationError(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )

    return True


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]

    # Remove dangerous characters
    filename = re.sub(r"[^a-zA-Z0-9\-_\.]", "_", filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename


def validate_analysis_id(analysis_id):
    """Validate analysis ID format"""
    uuid_pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    if not re.match(uuid_pattern, analysis_id):
        raise ValidationError("Invalid analysis ID format")
    return True
