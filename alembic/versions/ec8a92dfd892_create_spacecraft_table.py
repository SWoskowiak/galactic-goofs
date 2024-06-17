"""create spacecraft table

Revision ID: ec8a92dfd892
Revises:
Create Date: 2024-06-15 12:21:53.600669

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec8a92dfd892"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # UUIDs are a seperate pg extension we want to enable
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    # Spacecraft status can just be an enum in here for now, typically this is a great candidate for a seed file that regenerates on deploy
    op.execute("""
        DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'spacecraft_status') THEN
                    CREATE TYPE spacecraft_status AS ENUM ('NONE', 'NOMINAL', 'MALFUNCTIONING');
                END IF;
            END
        $$;
    """)
    # Create update time trigger in postgres
    op.execute("""
        CREATE OR REPLACE FUNCTION update_time()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.update_time = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    # Spacecraft table
    op.execute("""
    CREATE TABLE IF NOT EXISTS spacecraft (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        status spacecraft_status NOT NULL DEFAULT 'NONE',
        cospar_id VARCHAR(50) NOT NULL,
        uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
        create_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        update_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TRIGGER spacecraft_update_time
    BEFORE UPDATE ON spacecraft
    FOR EACH ROW
    EXECUTE FUNCTION update_time();
    """)
    # Simple index on uuid for spacecraft
    op.execute("CREATE INDEX IF NOT EXISTS idx_spacecraft_uuid ON spacecraft (uuid)")


def downgrade():
    op.execute("DROP INDEX idx_spacecraft_uuid")
    op.execute("DROP TABLE spacecraft")
    op.execute("DROP TYPE spacecraft_status")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute("DROP FUNCTION IF EXISTS update_time()")
    op.execute("DROP TRIGGER IF EXISTS spacecraft_update_time ON spacecraft")
