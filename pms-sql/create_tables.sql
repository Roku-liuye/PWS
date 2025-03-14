-- 创建数据库
-- 数据库位置locallhost:3306 - uroot -p123456'
CREATE DATABASE IF NOT EXISTS pms_db;
USE pms_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(255),
    role ENUM('admin', 'staff', 'teacher', 'student') NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 资产表
CREATE TABLE IF NOT EXISTS assets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    purchase_date DATE,
    lifespan VARCHAR(20),
    status ENUM('normal', 'repair', 'scrapped') NOT NULL DEFAULT 'normal',
    description TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 报修表
CREATE TABLE IF NOT EXISTS repairs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('equipment', 'facility') NOT NULL,
    asset_id INT(20),
    location VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    submitter_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    complete_time DATETIME,
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (submitter_id) REFERENCES users(id)
);

-- 维修分配表
CREATE TABLE IF NOT EXISTS maintenance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    repair_id INT NOT NULL,
    maintainer_id INT NOT NULL,
    assign_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    expected_time DATETIME,
    actual_time DATETIME,
    result TEXT,
    FOREIGN KEY (repair_id) REFERENCES repairs(id),
    FOREIGN KEY (maintainer_id) REFERENCES users(id)
);

-- 费用表
CREATE TABLE IF NOT EXISTS finances (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('repair', 'purchase', 'maintenance', 'other') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    operator_id INT NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id)
);

-- 教室表
CREATE TABLE IF NOT EXISTS classrooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_no VARCHAR(20) NOT NULL UNIQUE,
    building VARCHAR(50) NOT NULL,
    type ENUM('multimedia', 'normal') NOT NULL,
    capacity INT NOT NULL,
    facilities TEXT,
    status ENUM('available', 'booked', 'maintenance') NOT NULL DEFAULT 'available'
);

-- 教室预约表
CREATE TABLE IF NOT EXISTS classroom_bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    classroom_id INT NOT NULL,
    user_id INT NOT NULL,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    purpose VARCHAR(255),
    status ENUM('pending', 'approved', 'rejected', 'cancelled') NOT NULL DEFAULT 'pending',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 公告表
CREATE TABLE IF NOT EXISTS notices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    publisher_id INT NOT NULL,
    publish_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'published',
    FOREIGN KEY (publisher_id) REFERENCES users(id)
);