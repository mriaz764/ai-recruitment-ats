from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.organizations.models import (
    Membership,
    Organization,
    User,
)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def get_membership_and_organization(
    db: Session,
    user_id: int,
    organization_id: int | None = None,
) -> tuple[Membership, Organization] | None:
    statement = (
        select(Membership, Organization)
        .join(Organization, Organization.id == Membership.organization_id)
        .where(Membership.user_id == user_id)
        .order_by(Membership.id)
    )

    if organization_id is not None:
        statement = statement.where(Membership.organization_id == organization_id)

    row = db.execute(statement).first()
    if row is None:
        return None

    return row[0], row[1]
