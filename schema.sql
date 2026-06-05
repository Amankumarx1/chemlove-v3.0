-- ============================================================
-- ChemLove v2 — Optimised MySQL Schema
-- Run once in the MySQL Command Line or Query Browser.
-- Only transactional / user-specific data lives here.
-- Static content (chapters, labs, badges, quizzes) lives in
-- content/ JSON files and is served directly by Flask.
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS user_history;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS user_badges;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS test_attempts;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS classrooms;
DROP TABLE IF EXISTS teacher_profiles;
DROP TABLE IF EXISTS student_profiles;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ── 1. USERS ────────────────────────────────────────────────
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(512) NOT NULL,
    institution   VARCHAR(255) NOT NULL,
    role          VARCHAR(50)  NOT NULL,
    class_level   VARCHAR(50),
    status        VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_role CHECK (role IN ('student', 'teacher', 'admin')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'suspended'))
);

-- ── 2. STUDENT PROFILES ────────────────────────────────────
CREATE TABLE student_profiles (
    user_id     INT PRIMARY KEY,
    current_xp  INT NOT NULL DEFAULT 100,
    level       INT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 3. TEACHER PROFILES ────────────────────────────────────
CREATE TABLE teacher_profiles (
    user_id        INT PRIMARY KEY,
    department     VARCHAR(255) NOT NULL DEFAULT 'Chemistry',
    qualifications TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 4. CLASSROOMS ──────────────────────────────────────────
CREATE TABLE classrooms (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    teacher_id  INT          NOT NULL,
    grade       VARCHAR(50)  NOT NULL,
    section     VARCHAR(50),
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 5. ENROLLMENTS ─────────────────────────────────────────
CREATE TABLE enrollments (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT NOT NULL,
    student_id   INT NOT NULL,
    enrolled_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (classroom_id, student_id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 6. ASSIGNMENTS ─────────────────────────────────────────
CREATE TABLE assignments (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    description  TEXT,
    classroom_id INT          NOT NULL,
    chapter_id   INT,                       
    lab_id       INT,                       
    marks        INT          NOT NULL DEFAULT 100,
    due_date     TIMESTAMP    NULL,
    instructions TEXT,
    status       VARCHAR(50)  NOT NULL DEFAULT 'draft',
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_assignment_status CHECK (status IN ('draft', 'published', 'archived')),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE
);

-- ── 7. SUBMISSIONS ─────────────────────────────────────────
CREATE TABLE submissions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id  INT  NOT NULL,
    student_id     INT  NOT NULL,
    submitted_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_data      TEXT,
    marks_obtained FLOAT,
    feedback       TEXT,
    status         VARCHAR(50) NOT NULL DEFAULT 'pending',
    UNIQUE (assignment_id, student_id),
    CONSTRAINT chk_submission_status CHECK (status IN ('pending', 'graded', 'approved')),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 8. TESTS ───────────────────────────────────────────────
CREATE TABLE tests (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    title            VARCHAR(255) NOT NULL,
    classroom_id     INT          NOT NULL,
    chapter_id       INT,                  
    quiz_content_id  INT,                  
    duration_minutes INT          NOT NULL DEFAULT 30,
    total_marks      INT          NOT NULL DEFAULT 100,
    start_date       TIMESTAMP    NULL,
    end_date         TIMESTAMP    NULL,
    difficulty       VARCHAR(50)  NOT NULL DEFAULT 'medium',
    status           VARCHAR(50)  NOT NULL DEFAULT 'scheduled',
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_test_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard')),
    CONSTRAINT chk_test_status CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled')),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE
);

-- ── 9. TEST ATTEMPTS ───────────────────────────────────────
CREATE TABLE test_attempts (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    test_id                 INT  NOT NULL,
    student_id              INT  NOT NULL,
    score                   FLOAT,
    started_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at            TIMESTAMP NULL,
    status                  VARCHAR(50) NOT NULL DEFAULT 'completed',
    suspicious_alerts_count INT  NOT NULL DEFAULT 0,
    UNIQUE (test_id, student_id),
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 10. ANNOUNCEMENTS ─────────────────────────────────────
CREATE TABLE announcements (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    content      TEXT         NOT NULL,
    author_id    INT          NOT NULL,
    classroom_id INT,
    target_role  VARCHAR(50),
    is_pinned    BOOLEAN      NOT NULL DEFAULT FALSE,
    publish_at   TIMESTAMP    NULL,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE
);

-- ── 11. USER BADGES ────────────────────────────────────────
CREATE TABLE user_badges (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT  NOT NULL,
    badge_id    INT  NOT NULL,              
    unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 12. ATTENDANCE ────────────────────────────────────────
CREATE TABLE attendance (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT  NOT NULL,
    student_id   INT  NOT NULL,
    date         DATE NOT NULL,
    status       VARCHAR(50) NOT NULL,
    UNIQUE (classroom_id, student_id, date),
    CONSTRAINT chk_attendance_status CHECK (status IN ('present', 'absent', 'late')),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── 13. USER HISTORY ──────────────────────────────────────
CREATE TABLE user_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT  NOT NULL,
    event_type  VARCHAR(255) NOT NULL,
    event_data  TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── INDEXES ────────────────────────────────────────────────
CREATE INDEX idx_user_history_user_id ON user_history(user_id);
CREATE INDEX idx_user_history_created_at ON user_history(created_at);
CREATE INDEX idx_enrollments_student    ON enrollments(student_id);
CREATE INDEX idx_enrollments_classroom  ON enrollments(classroom_id);
CREATE INDEX idx_submissions_student    ON submissions(student_id);
CREATE INDEX idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX idx_test_attempts_student  ON test_attempts(student_id);
CREATE INDEX idx_test_attempts_test     ON test_attempts(test_id);

-- ── SEED: Default Admin ────────────────────────────────────
INSERT IGNORE INTO users (name, email, password_hash, institution, role, status)
VALUES ('Admin', 'admin@chemlove.com', 'scrypt:32768:8:1$y5Y3twDBqUM20pnR$10eabc09d6246b3dd23c9806688da459046ffd056e902ff23b6d1f5c94de666a1bcd52595aedb0d0ab71111e24ce825f7c5f05c2ba0d0a483e1bdf6f98d3fb90', 'ChemLove', 'admin', 'active');
