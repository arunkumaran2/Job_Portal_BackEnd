-- Full Job Portal schema. Safe to re-run (IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(150) NOT NULL UNIQUE,
    mobile_number VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'job_seeker',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_seekers (
    job_seeker_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    email VARCHAR(150) NOT NULL UNIQUE,
    mobile_number VARCHAR(20) UNIQUE,

    date_of_birth DATE,
    gender VARCHAR(20),

    location VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),

    profile_summary TEXT,

    total_experience DECIMAL(4,1) DEFAULT 0.0,

    current_company VARCHAR(150),
    current_job_title VARCHAR(150),

    expected_salary DECIMAL(12,2),
    notice_period INT,

    resume_url VARCHAR(255),
    profile_photo VARCHAR(255),

    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS recruiters (
    recruiter_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,

    designation VARCHAR(100),
    department VARCHAR(100),

    company_name VARCHAR(200) NOT NULL,
    company_email VARCHAR(150),
    company_phone VARCHAR(20),

    company_website VARCHAR(255),
    company_description TEXT,

    industry VARCHAR(100),
    company_size VARCHAR(50),
    company_type VARCHAR(100),

    location VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',

    company_logo VARCHAR(255),

    linkedin_url VARCHAR(255),

    is_verified BOOLEAN DEFAULT FALSE,
    status ENUM('Active', 'Inactive', 'Blocked') DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,

    password VARCHAR(255) NOT NULL,

    role ENUM('SUPER_ADMIN', 'ADMIN') DEFAULT 'ADMIN',

    status ENUM('ACTIVE', 'INACTIVE', 'BLOCKED')
        DEFAULT 'ACTIVE',

    last_login DATETIME,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    recruiter_id INT NOT NULL,

    job_title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,

    company_name VARCHAR(200) NOT NULL,

    job_type ENUM(
        'Full-Time',
        'Part-Time',
        'Contract',
        'Internship',
        'Freelance'
    ) DEFAULT 'Full-Time',

    work_mode ENUM(
        'Onsite',
        'Remote',
        'Hybrid'
    ) DEFAULT 'Onsite',

    experience_min INT DEFAULT 0,
    experience_max INT,

    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    salary_type ENUM('Monthly', 'Yearly'),

    location VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',

    education_required VARCHAR(255),
    department VARCHAR(100),
    industry VARCHAR(100),

    openings INT DEFAULT 1,

    application_deadline DATE,

    status ENUM(
        'Draft',
        'Active',
        'Closed',
        'Expired'
    ) DEFAULT 'Draft',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (recruiter_id)
        REFERENCES recruiters(recruiter_id)
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_skill_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,

    skill_name VARCHAR(100) NOT NULL,
    skill_level ENUM(
        'Beginner',
        'Intermediate',
        'Advanced'
    ) DEFAULT 'Intermediate',

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,

    category_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    status ENUM('Active', 'Inactive')
        DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_category_mapping (
    job_id INT NOT NULL,
    category_id INT NOT NULL,

    PRIMARY KEY (job_id, category_id),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (category_id)
        REFERENCES job_categories(category_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,

    job_id INT NOT NULL,
    job_seeker_id INT NOT NULL,

    cover_letter TEXT,

    status ENUM(
        'Applied',
        'Shortlisted',
        'Rejected',
        'Interview',
        'Selected',
        'Withdrawn'
    ) DEFAULT 'Applied',

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_seeker_id)
        REFERENCES job_seekers(job_seeker_id)
        ON DELETE CASCADE,

    UNIQUE (job_id, job_seeker_id)
);

CREATE TABLE IF NOT EXISTS saved_jobs (
    saved_job_id INT PRIMARY KEY AUTO_INCREMENT,

    job_id INT NOT NULL,
    job_seeker_id INT NOT NULL,

    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_seeker_id)
        REFERENCES job_seekers(job_seeker_id)
        ON DELETE CASCADE,

    UNIQUE (job_id, job_seeker_id)
);
