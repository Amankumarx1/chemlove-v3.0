-- ============================================================
-- ChemLove v2 — Optimised MySQL Schema
-- Run once in the MySQL Command Line or Query Browser.
-- Only transactional / user-specific data lives here.
-- Static content (chapters, labs, badges, quizzes) lives in
-- content/ JSON files and is served directly by Flask.
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS teacher_courses;
DROP TABLE IF EXISTS course_enrollments;
DROP TABLE IF EXISTS certificates;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS lessons;
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
DROP TABLE IF EXISTS quiz_questions;
DROP TABLE IF EXISTS quizzes;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS reactions;
DROP TABLE IF EXISTS badges;
DROP TABLE IF EXISTS labs;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS categories;
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
    CONSTRAINT chk_role CHECK (role IN ('student', 'teacher', 'admin', 'superadmin')),
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

-- ── 3.5. SYLLABUS & STATIC CONTENT ───────────────────────────
CREATE TABLE chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_level VARCHAR(50),
    chapter_number INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    learning_objectives JSON,
    key_points JSON,
    important_laws JSON,
    formulas JSON,
    constants JSON,
    important_reactions JSON,
    notes JSON,
    real_life_applications JSON,
    virtual_labs JSON,
    practice_questions JSON,
    common_mistakes JSON,
    difficulty VARCHAR(50),
    estimated_study_time VARCHAR(50),
    chapter_weightage JSON,
    next_chapter JSON,
    quiz_id INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE labs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    chapter_id INT,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'published',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE badges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    xp_reward INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reactions (
    id VARCHAR(50) PRIMARY KEY,
    chapter_id INT,
    class_level VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    equation TEXT,
    reaction_type VARCHAR(100),
    reactants JSON,
    products JSON,
    conditions VARCHAR(255),
    explanation LONGTEXT,
    mechanism JSON,
    applications LONGTEXT,
    not_occur LONGTEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE experiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT,
    title VARCHAR(255) NOT NULL,
    aim LONGTEXT,
    apparatus JSON,
    theory LONGTEXT,
    `procedure` JSON,
    observations JSON,
    result LONGTEXT,
    viva_questions JSON,
    simulation_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT,
    title VARCHAR(255) NOT NULL,
    total_marks INT NOT NULL DEFAULT 100,
    duration_minutes INT NOT NULL DEFAULT 30,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE TABLE quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question LONGTEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    explanation LONGTEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
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
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL,
    FOREIGN KEY (lab_id) REFERENCES labs(id) ON DELETE SET NULL
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
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
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


-- ── 14. COURSES & CATEGORIES ──────────────────────────────────
CREATE TABLE categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE courses (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    category      VARCHAR(100),
    class_level   VARCHAR(50),
    status        VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_course_status CHECK (status IN ('active', 'archived'))
);

CREATE TABLE modules (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_id   INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INT DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Alter chapters to link to a module (nullable for backward compatibility)
ALTER TABLE chapters ADD COLUMN module_id INT NULL;
ALTER TABLE chapters ADD CONSTRAINT fk_chapter_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL;


-- ── 15. LESSONS & RESOURCES ──────────────────────────────────
CREATE TABLE lessons (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id  INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    content     TEXT,
    order_index INT DEFAULT 0,
    status      VARCHAR(50) NOT NULL DEFAULT 'published',
    publish_at  TIMESTAMP NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_lesson_status CHECK (status IN ('draft', 'published', 'scheduled')),
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
);

CREATE TABLE resources (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    lesson_id   INT,
    title       VARCHAR(255) NOT NULL,
    file_path   VARCHAR(500) NOT NULL,
    file_type   VARCHAR(50) NOT NULL, -- 'pdf', 'video', 'ppt', 'image', 'zip', 'link'
    status      VARCHAR(50) NOT NULL DEFAULT 'published',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_resource_status CHECK (status IN ('draft', 'published', 'archived')),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);


-- ── 16. ENROLLMENTS & TEACHERS ─────────────────────────────────
CREATE TABLE course_enrollments (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    course_id    INT NOT NULL,
    student_id   INT NOT NULL,
    progress     INT DEFAULT 0,
    status       VARCHAR(50) NOT NULL DEFAULT 'active',
    enrolled_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    UNIQUE (course_id, student_id),
    CONSTRAINT chk_enrollment_status CHECK (status IN ('active', 'completed')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE teacher_courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_id   INT NOT NULL,
    teacher_id  INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (course_id, teacher_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
);


-- ── 17. CERTIFICATES & NOTIFICATIONS ───────────────────────────
CREATE TABLE certificates (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    course_id       INT NOT NULL,
    verification_id VARCHAR(100) NOT NULL UNIQUE,
    issued_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(50) NOT NULL DEFAULT 'issued',
    CONSTRAINT chk_certificate_status CHECK (status IN ('issued', 'revoked')),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    sender_id    INT NOT NULL,
    recipient_id INT NULL,
    target_group VARCHAR(100) NULL,
    title        VARCHAR(255) NOT NULL,
    message      TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);


-- ── 18. AUDIT LOGS & PERMISSIONS ──────────────────────────────
CREATE TABLE audit_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    action     VARCHAR(255) NOT NULL,
    details    TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE permissions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    role           VARCHAR(50) NOT NULL,
    permission_key VARCHAR(100) NOT NULL,
    is_granted     BOOLEAN DEFAULT TRUE,
    UNIQUE (role, permission_key)
);

-- Seed default permissions for Admin role
INSERT IGNORE INTO permissions (role, permission_key, is_granted) VALUES
('admin', 'manage_users', TRUE),
('admin', 'manage_content', TRUE),
('admin', 'manage_assessments', TRUE),
('admin', 'manage_certificates', TRUE),
('admin', 'send_notifications', TRUE),
('admin', 'view_reports', TRUE);

