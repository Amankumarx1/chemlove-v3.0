SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `activity_logs`;
DROP TABLE IF EXISTS `announcements`;
DROP TABLE IF EXISTS `assessment_progress`;
DROP TABLE IF EXISTS `assignments`;
DROP TABLE IF EXISTS `attendance`;
DROP TABLE IF EXISTS `audit_logs`;
DROP TABLE IF EXISTS `badges`;
DROP TABLE IF EXISTS `batches`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `certificate_templates`;
DROP TABLE IF EXISTS `certificates`;
DROP TABLE IF EXISTS `chapter_progress`;
DROP TABLE IF EXISTS `chapter_section_progress`;
DROP TABLE IF EXISTS `chapters`;
DROP TABLE IF EXISTS `classrooms`;
DROP TABLE IF EXISTS `content_versions`;
DROP TABLE IF EXISTS `course_enrollments`;
DROP TABLE IF EXISTS `course_progress`;
DROP TABLE IF EXISTS `courses`;
DROP TABLE IF EXISTS `dashboard_widgets`;
DROP TABLE IF EXISTS `enrollments`;
DROP TABLE IF EXISTS `experiments`;
DROP TABLE IF EXISTS `lab_attempts`;
DROP TABLE IF EXISTS `labs`;
DROP TABLE IF EXISTS `lesson_progress`;
DROP TABLE IF EXISTS `lessons`;
DROP TABLE IF EXISTS `library_settings`;
DROP TABLE IF EXISTS `modules`;
DROP TABLE IF EXISTS `notification_reads`;
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `permissions`;
DROP TABLE IF EXISTS `quiz_questions`;
DROP TABLE IF EXISTS `quizzes`;
DROP TABLE IF EXISTS `reactions`;
DROP TABLE IF EXISTS `resources`;
DROP TABLE IF EXISTS `schools`;
DROP TABLE IF EXISTS `student_profiles`;
DROP TABLE IF EXISTS `subjects`;
DROP TABLE IF EXISTS `submissions`;
DROP TABLE IF EXISTS `teacher_courses`;
DROP TABLE IF EXISTS `teacher_profiles`;
DROP TABLE IF EXISTS `test_attempts`;
DROP TABLE IF EXISTS `tests`;
DROP TABLE IF EXISTS `user_badges`;
DROP TABLE IF EXISTS `user_history`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;


SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `activity_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_type` varchar(255) NOT NULL,
  `event_data` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `announcements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `author_id` int NOT NULL,
  `classroom_id` int DEFAULT NULL,
  `target_role` varchar(50) DEFAULT NULL,
  `is_pinned` tinyint(1) NOT NULL DEFAULT '0',
  `publish_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `announcements_ibfk_2` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `assessment_progress` (
  `user_id` int NOT NULL,
  `assessment_type` varchar(50) NOT NULL,
  `assessment_id` int NOT NULL,
  `score_percentage` decimal(5,2) DEFAULT '0.00',
  `attempts_count` int DEFAULT '1',
  `is_passed` tinyint(1) DEFAULT '0',
  `last_attempt_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`assessment_type`,`assessment_id`),
  CONSTRAINT `assessment_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `title` varchar(255) NOT NULL,
  `description` text,
  `classroom_id` int NOT NULL,
  `chapter_id` int DEFAULT NULL,
  `lab_id` int DEFAULT NULL,
  `marks` int NOT NULL DEFAULT '100',
  `due_date` timestamp NULL DEFAULT NULL,
  `instructions` text,
  `status` varchar(50) NOT NULL DEFAULT 'draft',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `chapter_id` (`chapter_id`),
  KEY `lab_id` (`lab_id`),
  CONSTRAINT `assignments_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `assignments_ibfk_2` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL,
  CONSTRAINT `assignments_ibfk_3` FOREIGN KEY (`lab_id`) REFERENCES `labs` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_assignment_status` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'published',_utf8mb4'archived')))
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `student_id` int NOT NULL,
  `date` date NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `classroom_id` (`classroom_id`,`student_id`,`date`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_attendance_status` CHECK ((`status` in (_utf8mb4'present',_utf8mb4'absent',_utf8mb4'late')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(255) NOT NULL,
  `details` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `name` varchar(255) NOT NULL,
  `description` text,
  `icon` varchar(100) DEFAULT NULL,
  `xp_reward` int NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `batches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `batches_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `certificate_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `html_layout` longtext NOT NULL,
  `css_styles` longtext NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `certificates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `verification_id` varchar(100) NOT NULL,
  `issued_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) NOT NULL DEFAULT 'issued',
  `template_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `verification_id` (`verification_id`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_id`),
  KEY `fk_cert_template` (`template_id`),
  CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `certificates_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cert_template` FOREIGN KEY (`template_id`) REFERENCES `certificate_templates` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_certificate_status` CHECK ((`status` in (_utf8mb4'issued',_utf8mb4'revoked')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `chapter_progress` (
  `user_id` int NOT NULL,
  `chapter_id` int NOT NULL,
  `is_completed` tinyint(1) DEFAULT '0',
  `completed_at` timestamp NULL DEFAULT NULL,
  `overview_completed` tinyint(1) DEFAULT '0',
  `keypoints_completed` tinyint(1) DEFAULT '0',
  `formulas_completed` tinyint(1) DEFAULT '0',
  `reactions_completed` tinyint(1) DEFAULT '0',
  `experiments_completed` tinyint(1) DEFAULT '0',
  `practice_completed` tinyint(1) DEFAULT '0',
  `quiz_completed` tinyint(1) DEFAULT '0',
  `completion_percentage` int DEFAULT '0',
  `xp_earned` int DEFAULT '0',
  PRIMARY KEY (`user_id`,`chapter_id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `chapter_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chapter_progress_ibfk_2` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `chapter_section_progress` (
  `user_id` int NOT NULL,
  `chapter_id` int NOT NULL,
  `section_name` varchar(50) NOT NULL,
  `is_completed` tinyint(1) DEFAULT '0',
  `completed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`chapter_id`,`section_name`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `chapter_section_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chapter_section_progress_ibfk_2` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `chapters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `class_level` varchar(50) DEFAULT NULL,
  `chapter_number` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `learning_objectives` json DEFAULT NULL,
  `key_points` longtext,
  `important_laws` json DEFAULT NULL,
  `formulas` longtext,
  `constants` json DEFAULT NULL,
  `important_reactions` json DEFAULT NULL,
  `notes` longtext,
  `real_life_applications` json DEFAULT NULL,
  `virtual_labs` json DEFAULT NULL,
  `practice_questions` json DEFAULT NULL,
  `common_mistakes` json DEFAULT NULL,
  `difficulty` varchar(50) DEFAULT NULL,
  `estimated_study_time` varchar(50) DEFAULT NULL,
  `chapter_weightage` json DEFAULT NULL,
  `next_chapter` json DEFAULT NULL,
  `quiz_id` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `module_id` int DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'draft',
  `version` int DEFAULT '1',
  `order_index` int DEFAULT '0',
  `publish_at` timestamp NULL DEFAULT NULL,
  `course_id` int DEFAULT NULL,
  `reactions` longtext,
  `experiment_content` longtext,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `overview_content` longtext,
  `key_points_content` longtext,
  `formula_content` longtext,
  `reaction_content` longtext,
  `practice_content` longtext,
  PRIMARY KEY (`id`),
  KEY `fk_chapter_module` (`module_id`),
  KEY `fk_chapters_course` (`course_id`),
  CONSTRAINT `fk_chapter_module` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_chapters_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `classrooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `teacher_id` int NOT NULL,
  `grade` varchar(50) NOT NULL,
  `section` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `classrooms_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `content_versions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content_type` varchar(50) NOT NULL,
  `content_id` int NOT NULL,
  `version_number` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `content_data` longtext NOT NULL,
  `created_by` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type` (`content_type`,`content_id`,`version_number`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `content_versions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `course_enrollments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `student_id` int NOT NULL,
  `progress` int DEFAULT '0',
  `status` varchar(50) NOT NULL DEFAULT 'active',
  `enrolled_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_id` (`course_id`,`student_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `course_enrollments_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `course_enrollments_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_enrollment_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'completed')))
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `course_progress` (
  `user_id` int NOT NULL,
  `course_id` int NOT NULL,
  `percent_completed` decimal(5,2) DEFAULT '0.00',
  `last_accessed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `course_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `course_progress_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `title` varchar(255) NOT NULL,
  `description` text,
  `category` varchar(100) DEFAULT NULL,
  `class_level` varchar(50) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'draft',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `thumbnail` varchar(500) DEFAULT NULL,
  `version` int DEFAULT '1',
  `published_at` timestamp NULL DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_course_subject` (`subject_id`),
  CONSTRAINT `fk_course_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_course_status` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'review',_utf8mb4'published',_utf8mb4'archived',_utf8mb4'active')))
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `dashboard_widgets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `widget_key` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `is_enabled` tinyint(1) NOT NULL DEFAULT '1',
  `sort_order` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `widget_key` (`widget_key`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `enrollments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `classroom_id` int NOT NULL,
  `student_id` int NOT NULL,
  `enrolled_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `classroom_id` (`classroom_id`,`student_id`),
  KEY `idx_enrollments_student` (`student_id`),
  KEY `idx_enrollments_classroom` (`classroom_id`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `experiments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `chapter_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `aim` longtext,
  `apparatus` json DEFAULT NULL,
  `theory` longtext,
  `procedure` json DEFAULT NULL,
  `observations` json DEFAULT NULL,
  `result` longtext,
  `viva_questions` json DEFAULT NULL,
  `simulation_url` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `experiments_ibfk_1` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `lab_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `experiment_name` varchar(255) NOT NULL,
  `mode` varchar(50) NOT NULL,
  `duration_seconds` int NOT NULL,
  `mistakes_count` int NOT NULL DEFAULT '0',
  `accuracy_percentage` int NOT NULL DEFAULT '100',
  `completed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `lab_attempts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `labs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `title` varchar(255) NOT NULL,
  `chapter_id` int DEFAULT NULL,
  `description` text,
  `status` varchar(50) NOT NULL DEFAULT 'published',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `labs_ibfk_1` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `lesson_progress` (
  `user_id` int NOT NULL,
  `lesson_id` int NOT NULL,
  `is_completed` tinyint(1) DEFAULT '0',
  `time_spent_seconds` int DEFAULT '0',
  `last_accessed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`lesson_id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `lesson_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `lesson_progress_ibfk_2` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `lessons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `chapter_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text,
  `order_index` int DEFAULT '0',
  `status` varchar(50) NOT NULL DEFAULT 'published',
  `publish_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `version` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `lessons_ibfk_1` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_lesson_status` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'review',_utf8mb4'published',_utf8mb4'archived')))
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `library_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL,
  `access_mode` varchar(50) NOT NULL DEFAULT 'OPEN',
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `order_index` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `modules_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `notification_reads` (
  `user_id` int NOT NULL,
  `notification_id` int NOT NULL,
  `read_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`notification_id`),
  KEY `notification_id` (`notification_id`),
  CONSTRAINT `notification_reads_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `notification_reads_ibfk_2` FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `recipient_id` int DEFAULT NULL,
  `target_group` varchar(100) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `target_role` varchar(50) DEFAULT 'all',
  `target_institution` varchar(255) DEFAULT 'all',
  `target_class_level` varchar(50) DEFAULT 'all',
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role` varchar(50) NOT NULL,
  `permission_key` varchar(100) NOT NULL,
  `is_granted` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `role` (`role`,`permission_key`)
) ENGINE=InnoDB AUTO_INCREMENT=143 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `quiz_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quiz_id` int NOT NULL,
  `question` longtext NOT NULL,
  `option_a` text NOT NULL,
  `option_b` text NOT NULL,
  `option_c` text NOT NULL,
  `option_d` text NOT NULL,
  `correct_answer` char(1) NOT NULL,
  `explanation` longtext,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `quiz_id` (`quiz_id`),
  CONSTRAINT `quiz_questions_ibfk_1` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `quizzes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `chapter_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `total_marks` int NOT NULL DEFAULT '100',
  `duration_minutes` int NOT NULL DEFAULT '30',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `quizzes_ibfk_1` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `reactions` (
  `id` varchar(50) NOT NULL,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `chapter_id` int DEFAULT NULL,
  `class_level` varchar(50) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `equation` text,
  `reaction_type` varchar(100) DEFAULT NULL,
  `reactants` json DEFAULT NULL,
  `products` json DEFAULT NULL,
  `conditions` varchar(255) DEFAULT NULL,
  `explanation` longtext,
  `mechanism` json DEFAULT NULL,
  `applications` longtext,
  `not_occur` longtext,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `reactions_ibfk_1` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `resources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lesson_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'published',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `lesson_id` (`lesson_id`),
  CONSTRAINT `resources_ibfk_1` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_resource_status` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'published',_utf8mb4'archived')))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `schools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `access_mode` varchar(50) DEFAULT 'STRICT',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `student_profiles` (
  `user_id` int NOT NULL,
  `current_xp` int NOT NULL DEFAULT '100',
  `level` int NOT NULL DEFAULT '1',
  `streak_count` int NOT NULL DEFAULT '0',
  `last_active_date` date DEFAULT NULL,
  `last_chapter_id` int DEFAULT NULL,
  `last_experiment_id` int DEFAULT NULL,
  `last_assessment_id` int DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `fk_sp_last_chapter` (`last_chapter_id`),
  KEY `fk_sp_last_experiment` (`last_experiment_id`),
  KEY `fk_sp_last_assessment` (`last_assessment_id`),
  CONSTRAINT `fk_sp_last_assessment` FOREIGN KEY (`last_assessment_id`) REFERENCES `quizzes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_sp_last_chapter` FOREIGN KEY (`last_chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_sp_last_experiment` FOREIGN KEY (`last_experiment_id`) REFERENCES `experiments` (`id`) ON DELETE SET NULL,
  CONSTRAINT `student_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL,
  `student_id` int NOT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `file_data` text,
  `marks_obtained` float DEFAULT NULL,
  `feedback` text,
  `status` varchar(50) NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  UNIQUE KEY `assignment_id` (`assignment_id`,`student_id`),
  KEY `idx_submissions_student` (`student_id`),
  KEY `idx_submissions_assignment` (`assignment_id`),
  CONSTRAINT `submissions_ibfk_1` FOREIGN KEY (`assignment_id`) REFERENCES `assignments` (`id`) ON DELETE CASCADE,
  CONSTRAINT `submissions_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_submission_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'graded',_utf8mb4'approved')))
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `teacher_courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_id` (`course_id`,`teacher_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `teacher_courses_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `teacher_courses_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `teacher_profiles` (
  `user_id` int NOT NULL,
  `department` varchar(255) NOT NULL DEFAULT 'Chemistry',
  `qualifications` text,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `teacher_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `test_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` int NOT NULL,
  `student_id` int NOT NULL,
  `score` float DEFAULT NULL,
  `started_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'completed',
  `suspicious_alerts_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `test_id` (`test_id`,`student_id`),
  KEY `idx_test_attempts_student` (`student_id`),
  KEY `idx_test_attempts_test` (`test_id`),
  CONSTRAINT `test_attempts_ibfk_1` FOREIGN KEY (`test_id`) REFERENCES `tests` (`id`) ON DELETE CASCADE,
  CONSTRAINT `test_attempts_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `tests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `title` varchar(255) NOT NULL,
  `classroom_id` int NOT NULL,
  `chapter_id` int DEFAULT NULL,
  `quiz_content_id` int DEFAULT NULL,
  `duration_minutes` int NOT NULL DEFAULT '30',
  `total_marks` int NOT NULL DEFAULT '100',
  `start_date` timestamp NULL DEFAULT NULL,
  `end_date` timestamp NULL DEFAULT NULL,
  `difficulty` varchar(50) NOT NULL DEFAULT 'medium',
  `status` varchar(50) NOT NULL DEFAULT 'scheduled',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `tests_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `tests_ibfk_2` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_test_difficulty` CHECK ((`difficulty` in (_utf8mb4'easy',_utf8mb4'medium',_utf8mb4'hard'))),
  CONSTRAINT `chk_test_status` CHECK ((`status` in (_utf8mb4'scheduled',_utf8mb4'active',_utf8mb4'completed',_utf8mb4'cancelled')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `user_badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `badge_id` int NOT NULL,
  `unlocked_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`badge_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `user_badges_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_badges_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badges` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2047 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `user_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_type` varchar(255) NOT NULL,
  `event_data` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_history_user_id` (`user_id`),
  KEY `idx_user_history_created_at` (`created_at`),
  CONSTRAINT `user_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=611 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `public_id` varchar(36) NOT NULL UNIQUE,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(512) NOT NULL,
  `institution` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `class_level` varchar(50) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mobile` varchar(20) DEFAULT NULL,
  `avatar` varchar(100) DEFAULT 'account_circle',
  `failed_login_attempts` int NOT NULL DEFAULT 0,
  `lockout_until` timestamp NULL DEFAULT NULL,
  `last_login_at` timestamp NULL DEFAULT NULL,
  `password_changed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `chk_role` CHECK ((`role` in (_utf8mb4'student',_utf8mb4'teacher',_utf8mb4'admin',_utf8mb4'content_manager')))
) ENGINE=InnoDB AUTO_INCREMENT=156 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
