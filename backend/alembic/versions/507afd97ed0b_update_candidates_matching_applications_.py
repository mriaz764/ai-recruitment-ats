"""update_candidates_matching_applications_and_ai_subscriptions

Revision ID: 507afd97ed0b
Revises: 7b318a4761a3
Create Date: 2026-10-24 15:43:50.165698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '507afd97ed0b'
down_revision: Union[str, Sequence[str], None] = '7b318a4761a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. AI Usage Logs Table
    op.create_table(
        'ai_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('provider_used', sa.String(length=50), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_usage_logs_organization_id'), 'ai_usage_logs', ['organization_id'], unique=False)
    op.create_index(op.f('ix_ai_usage_logs_user_id'), 'ai_usage_logs', ['user_id'], unique=False)

    # 2. Organization AI Subscriptions Table
    op.create_table(
        'organization_ai_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('provider_type', sa.Enum('GEMINI_FLASH', 'GEMINI_PRO', 'OPENAI_MINI', 'OPENAI_GPT4O', name='aiprovidertype', native_enum=False), nullable=False),
        sa.Column('monthly_quota', sa.Integer(), nullable=False),
        sa.Column('used_this_month', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_ai_subscriptions_organization_id'), 'organization_ai_subscriptions', ['organization_id'], unique=True)

    # 3. Candidate Match Scores Table
    op.create_table(
        'candidate_match_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('is_knocked_out', sa.Boolean(), nullable=False),
        sa.Column('breakdown', sa.JSON(), nullable=True),
        sa.Column('ai_summary', sa.String(length=500), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'candidate_id', 'job_id', name='uq_candidate_job_match_score')
    )
    op.create_index(op.f('ix_candidate_match_scores_candidate_id'), 'candidate_match_scores', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_candidate_match_scores_job_id'), 'candidate_match_scores', ['job_id'], unique=False)
    op.create_index(op.f('ix_candidate_match_scores_organization_id'), 'candidate_match_scores', ['organization_id'], unique=False)

    # 4. Candidate Skills Table
    op.create_table(
        'candidate_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('proficiency_level', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidate_skills_candidate_id'), 'candidate_skills', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_candidate_skills_skill_name'), 'candidate_skills', ['skill_name'], unique=False)

    # 5. Applications Alterations
    op.add_column('applications', sa.Column('rejection_reason', sa.String(length=255), nullable=True))
    op.alter_column(
        'applications', 'status',
        existing_type=sa.VARCHAR(length=30),
        type_=sa.Enum('APPLIED', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED', 'REJECTED', name='applicationstatus', native_enum=False),
        existing_nullable=False,
        existing_server_default=sa.text("'applied'::character varying")
    )

    # 6. Candidate Resumes Alterations
    op.add_column('candidate_resumes', sa.Column('organization_id', sa.Integer(), nullable=False))
    op.add_column('candidate_resumes', sa.Column('parsed_json', sa.JSON(), nullable=True))
    op.add_column('candidate_resumes', sa.Column('parsing_status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'SKIPPED', name='parsingstatus', native_enum=False), nullable=False))
    op.create_index(op.f('ix_candidate_resumes_organization_id'), 'candidate_resumes', ['organization_id'], unique=False)
    op.create_foreign_key('fk_candidate_resumes_organization_id', 'candidate_resumes', 'organizations', ['organization_id'], ['id'], ondelete='RESTRICT')

    # 7. Candidates Alterations
    op.add_column('candidates', sa.Column('headline', sa.String(length=255), nullable=True))
    op.add_column('candidates', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('candidates', sa.Column('experience_years', sa.Float(), nullable=True))
    op.add_column('candidates', sa.Column('location', sa.String(length=150), nullable=True))
    op.add_column('candidates', sa.Column('creation_source', sa.Enum('MANUAL', 'AI_PARSED', 'AI_WITH_MANUAL_OVERRIDE', name='creationsource', native_enum=False), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('candidates', 'creation_source')
    op.drop_column('candidates', 'location')
    op.drop_column('candidates', 'experience_years')
    op.drop_column('candidates', 'summary')
    op.drop_column('candidates', 'headline')

    op.drop_constraint('fk_candidate_resumes_organization_id', 'candidate_resumes', type_='foreignkey')
    op.drop_index(op.f('ix_candidate_resumes_organization_id'), table_name='candidate_resumes')
    op.drop_column('candidate_resumes', 'parsing_status')
    op.drop_column('candidate_resumes', 'parsed_json')
    op.drop_column('candidate_resumes', 'organization_id')

    op.alter_column(
        'applications', 'status',
        existing_type=sa.Enum('APPLIED', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED', 'REJECTED', name='applicationstatus', native_enum=False),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
        existing_server_default=sa.text("'applied'::character varying")
    )
    op.drop_column('applications', 'rejection_reason')

    op.drop_index(op.f('ix_candidate_skills_skill_name'), table_name='candidate_skills')
    op.drop_index(op.f('ix_candidate_skills_candidate_id'), table_name='candidate_skills')
    op.drop_table('candidate_skills')

    op.drop_index(op.f('ix_candidate_match_scores_organization_id'), table_name='candidate_match_scores')
    op.drop_index(op.f('ix_candidate_match_scores_job_id'), table_name='candidate_match_scores')
    op.drop_index(op.f('ix_candidate_match_scores_candidate_id'), table_name='candidate_match_scores')
    op.drop_table('candidate_match_scores')

    op.drop_index(op.f('ix_organization_ai_subscriptions_organization_id'), table_name='organization_ai_subscriptions')
    op.drop_table('organization_ai_subscriptions')

    op.drop_index(op.f('ix_ai_usage_logs_user_id'), table_name='ai_usage_logs')
    op.drop_index(op.f('ix_ai_usage_logs_organization_id'), table_name='ai_usage_logs')
    op.drop_table('ai_usage_logs')