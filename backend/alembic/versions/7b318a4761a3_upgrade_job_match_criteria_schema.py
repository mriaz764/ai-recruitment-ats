"""upgrade_job_match_criteria_schema

Revision ID: 7b318a4761a3
Revises: 9b335856dabc
Create Date: 2026-10-24 01:51:57.981819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7b318a4761a3'
down_revision: Union[str, Sequence[str], None] = '9b335856dabc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_enum_if_not_exists(enum_name: str, values: tuple):
    """Safely create PostgreSQL ENUM types if they do not already exist."""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        formatted_values = ", ".join(f"'{v}'" for v in values)
        bind.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                        CREATE TYPE {enum_name} AS ENUM ({formatted_values});
                    END IF;
                END$$;
                """
            )
        )


def upgrade() -> None:
    # 1. Safely create ENUM types in Postgres
    create_enum_if_not_exists('hiringrole_enum', ('HIRING_MANAGER', 'RECRUITER', 'INTERVIEWER'))
    create_enum_if_not_exists('matchcategory_enum', ('SKILL', 'CERTIFICATION', 'EDUCATION', 'DOMAIN_KNOWLEDGE'))
    create_enum_if_not_exists('workmodel_enum', ('ON_SITE', 'HYBRID', 'REMOTE'))
    create_enum_if_not_exists('employmenttype_enum', ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'TEMPORARY'))
    create_enum_if_not_exists('experiencelevel_enum', ('ENTRY', 'MID', 'SENIOR', 'LEAD', 'EXECUTIVE'))
    create_enum_if_not_exists('jobstatus_enum', ('DRAFT', 'ACTIVE', 'ON_HOLD', 'CLOSED', 'ARCHIVED'))

    # Define Enum references with create_type=False so Alembic does not emit duplicate CREATE TYPE statements
    hiringrole_enum = postgresql.ENUM('HIRING_MANAGER', 'RECRUITER', 'INTERVIEWER', name='hiringrole_enum', create_type=False)
    matchcategory_enum = postgresql.ENUM('SKILL', 'CERTIFICATION', 'EDUCATION', 'DOMAIN_KNOWLEDGE', name='matchcategory_enum', create_type=False)
    workmodel_enum = postgresql.ENUM('ON_SITE', 'HYBRID', 'REMOTE', name='workmodel_enum', create_type=False)
    employmenttype_enum = postgresql.ENUM('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'TEMPORARY', name='employmenttype_enum', create_type=False)
    experiencelevel_enum = postgresql.ENUM('ENTRY', 'MID', 'SENIOR', 'LEAD', 'EXECUTIVE', name='experiencelevel_enum', create_type=False)
    jobstatus_enum = postgresql.ENUM('DRAFT', 'ACTIVE', 'ON_HOLD', 'CLOSED', 'ARCHIVED', name='jobstatus_enum', create_type=False)

    # 2. Create job_hiring_team table
    op.create_table('job_hiring_team',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', hiringrole_enum, nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Update job_match_criteria table safely
    op.add_column('job_match_criteria', sa.Column('keyword', sa.String(length=100), nullable=False, server_default=''))
    op.add_column('job_match_criteria', sa.Column('category', matchcategory_enum, nullable=False, server_default='SKILL'))
    op.add_column('job_match_criteria', sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.alter_column('job_match_criteria', 'weight',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Integer(),
               existing_nullable=False)
    
    op.drop_index(op.f('ix_job_match_criteria_id'), table_name='job_match_criteria', if_exists=True)
    op.drop_index(op.f('ix_job_match_criteria_organization_id'), table_name='job_match_criteria', if_exists=True)
    op.drop_column('job_match_criteria', 'organization_id')
    op.drop_column('job_match_criteria', 'criterion_name')
    op.drop_column('job_match_criteria', 'keywords')

    # 4. Add columns to jobs table
    op.add_column('jobs', sa.Column('code', sa.String(length=100), nullable=True))
    op.add_column('jobs', sa.Column('work_model', workmodel_enum, nullable=False, server_default='HYBRID'))
    op.add_column('jobs', sa.Column('employment_type', employmenttype_enum, nullable=False, server_default='FULL_TIME'))
    op.add_column('jobs', sa.Column('experience_level', experiencelevel_enum, nullable=False, server_default='MID'))
    op.add_column('jobs', sa.Column('status', jobstatus_enum, nullable=False, server_default='DRAFT'))
    op.add_column('jobs', sa.Column('requirements', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('benefits', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('salary_range', sa.JSON(), nullable=True))
    op.add_column('jobs', sa.Column('applicant_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('jobs', sa.Column('pipeline_id', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True))

    op.create_index(op.f('ix_jobs_code'), 'jobs', ['code'], unique=False)
    op.create_index(op.f('ix_jobs_department'), 'jobs', ['department'], unique=False)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_department'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_code'), table_name='jobs')

    op.drop_column('jobs', 'closed_at')
    op.drop_column('jobs', 'updated_at')
    op.drop_column('jobs', 'created_by_id')
    op.drop_column('jobs', 'pipeline_id')
    op.drop_column('jobs', 'applicant_count')
    op.drop_column('jobs', 'salary_range')
    op.drop_column('jobs', 'benefits')
    op.drop_column('jobs', 'requirements')
    op.drop_column('jobs', 'status')
    op.drop_column('jobs', 'experience_level')
    op.drop_column('jobs', 'employment_type')
    op.drop_column('jobs', 'work_model')
    op.drop_column('jobs', 'code')

    op.add_column('job_match_criteria', sa.Column('keywords', sa.TEXT(), autoincrement=False, nullable=False, server_default=''))
    op.add_column('job_match_criteria', sa.Column('criterion_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False, server_default=''))
    op.add_column('job_match_criteria', sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False, server_default='1'))

    op.alter_column('job_match_criteria', 'weight',
               existing_type=sa.Integer(),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)

    op.drop_column('job_match_criteria', 'is_required')
    op.drop_column('job_match_criteria', 'category')
    op.drop_column('job_match_criteria', 'keyword')

    op.drop_table('job_hiring_team')