"""Admin entity matching the admins table."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Admin:
    """Model/entity for an Admin user."""

    first_name: str
    email: str
    admin_id: Optional[int] = None
    user_id: Optional[int] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "ADMIN"
    status: str = "ACTIVE"
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Used only during save; never returned in API responses
    password: Optional[str] = field(default=None, repr=False)

    def to_dict(self, include_password: bool = False) -> dict[str, Any]:
        """Serialize the entity for API responses."""
        data = asdict(self)
        if not include_password:
            data.pop("password", None)

        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Admin":
        """Build an Admin from a database row mapping."""
        return cls(
            admin_id=row.get("admin_id"),
            user_id=row.get("user_id"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            email=row.get("email"),
            phone=row.get("phone"),
            role=row.get("role") or "ADMIN",
            status=row.get("status") or "ACTIVE",
            last_login=row.get("last_login"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
