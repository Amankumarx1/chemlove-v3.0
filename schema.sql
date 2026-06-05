-- ============================================================
-- ChemLove v2 — Optimised Supabase Schema
-- Run once in the Supabase SQL Editor.
-- Only transactional / user-specific data lives here.
-- Static content (chapters, labs, badges, quizzes) lives in
-- content/ JSON files and is served directly by Flask.
-- ============================================================

-- ── 1. USERS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    email       TEXT        NOT NULL UNIQUE,
    password_hash TEXT      NOT NULL,
    institution TEXT        NOT NULL,
    role        TEXT        NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    class_level TEXT,
    status      TEXT        NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 2. STUDENT PROFILES ────────────────────────────────────
CREATE TABLE IF NOT EXISTS student_profiles (
    user_id     INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_xp  INT NOT NULL DEFAULT 100,
    level       INT NOT NULL DEFAULT 1
);

-- ── 3. TEACHER PROFILES ────────────────────────────────────
CREATE TABLE IF NOT EXISTS teacher_profiles (
    user_id      INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    department   TEXT NOT NULL DEFAULT 'Chemistry',
    qualifications TEXT
);

-- ── 4. CLASSROOMS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS classrooms (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    teacher_id  INT         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    grade       TEXT        NOT NULL,
    section     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 5. ENROLLMENTS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id           SERIAL PRIMARY KEY,
    classroom_id INT NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    student_id   INT NOT NULL REFERENCES users(id)      ON DELETE CASCADE,
    enrolled_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (classroom_id, student_id)
);

-- ── 6. ASSIGNMENTS ─────────────────────────────────────────
-- chapter_id and lab_id are integer keys into the JSON files —
-- no FK needed since the source of truth is the file system.
CREATE TABLE IF NOT EXISTS assignments (
    id           SERIAL PRIMARY KEY,
    title        TEXT        NOT NULL,
    description  TEXT,
    classroom_id INT         NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    chapter_id   INT,                       -- ref into content/chapters/chapter_{id}.json
    lab_id       INT,                       -- ref into content/labs.json
    marks        INT         NOT NULL DEFAULT 100,
    due_date     TIMESTAMPTZ,
    instructions TEXT,
    status       TEXT        NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 7. SUBMISSIONS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS submissions (
    id            SERIAL PRIMARY KEY,
    assignment_id INT  NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id    INT  NOT NULL REFERENCES users(id)       ON DELETE CASCADE,
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_data     TEXT,
    marks_obtained REAL,
    feedback      TEXT,
    status        TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'graded', 'approved')),
    UNIQUE (assignment_id, student_id)
);

-- ── 8. TESTS ───────────────────────────────────────────────
-- Questions are stored in content/quizzes/{chapter_id}.json
-- Only the test metadata and results are persisted here.
CREATE TABLE IF NOT EXISTS tests (
    id               SERIAL PRIMARY KEY,
    title            TEXT        NOT NULL,
    classroom_id     INT         NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    chapter_id       INT,                  -- ref into content/chapters/
    quiz_content_id  INT,                  -- ref into content/quizzes/ json file id
    duration_minutes INT         NOT NULL DEFAULT 30,
    total_marks      INT         NOT NULL DEFAULT 100,
    start_date       TIMESTAMPTZ,
    end_date         TIMESTAMPTZ,
    difficulty       TEXT        NOT NULL DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    status           TEXT        NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 9. TEST ATTEMPTS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS test_attempts (
    id                      SERIAL PRIMARY KEY,
    test_id                 INT  NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    student_id              INT  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score                   REAL,
    started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at            TIMESTAMPTZ,
    status                  TEXT NOT NULL DEFAULT 'completed',
    suspicious_alerts_count INT  NOT NULL DEFAULT 0,
    UNIQUE (test_id, student_id)
);

-- ── 10. ANNOUNCEMENTS ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS announcements (
    id           SERIAL PRIMARY KEY,
    title        TEXT        NOT NULL,
    content      TEXT        NOT NULL,
    author_id    INT         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    classroom_id INT         REFERENCES classrooms(id) ON DELETE CASCADE,
    target_role  TEXT,
    is_pinned    BOOLEAN     NOT NULL DEFAULT FALSE,
    publish_at   TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 11. USER BADGES ────────────────────────────────────────
-- badge_id references the id field in content/badges.json
CREATE TABLE IF NOT EXISTS user_badges (
    id          SERIAL PRIMARY KEY,
    user_id     INT  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id    INT  NOT NULL,              -- ref into content/badges.json
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, badge_id)
);

-- ── 12. ATTENDANCE ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    id           SERIAL PRIMARY KEY,
    classroom_id INT  NOT NULL REFERENCES classrooms(id) ON DELETE CASCADE,
    student_id   INT  NOT NULL REFERENCES users(id)      ON DELETE CASCADE,
    date         DATE NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('present', 'absent', 'late')),
    UNIQUE (classroom_id, student_id, date)
);

-- ── 13. USER HISTORY (lean — key events only) ─────────────
-- Only meaningful events: login, signup, assignment_submit, test_submit
-- Old rows auto-purge after 30 days via a Supabase cron or pg_cron job.
CREATE TABLE IF NOT EXISTS user_history (
    id          SERIAL PRIMARY KEY,
    user_id     INT  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type  TEXT NOT NULL,
    event_data  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_history_created_at ON user_history(created_at);

-- ── INDEXES ────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_enrollments_student    ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_classroom  ON enrollments(classroom_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student    ON submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_test_attempts_student  ON test_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_test_attempts_test     ON test_attempts(test_id);

-- ── SEED: Default Admin ────────────────────────────────────
-- Password hash for 'admin123' — replace after first login!
-- Generate a real hash with: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"
INSERT INTO users (name, email, password_hash, institution, role, status)
VALUES ('Admin', 'admin@chemlove.com', 'pbkdf2:sha256:600000$replace_this_hash', 'ChemLove', 'admin', 'active')
ON CONFLICT (email) DO NOTHING;
