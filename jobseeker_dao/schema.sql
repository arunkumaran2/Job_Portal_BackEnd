-- Users table (auth credentials; referenced by job_seekers.user_id)
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
