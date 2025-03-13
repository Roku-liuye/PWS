USE pms_db;

-- 插入用户数据
INSERT INTO users (username, password, real_name, role, phone, email) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '管理员', 'admin', '13800000001', 'admin@pms.com'),
('staff0', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '工人', 'staff', '13800000011', 'stf0@pms.com'),
('teacher0', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '教师', 'teacher', '13800000111', 'tech0@pms.com'),
('student0', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '学生', 'student', '13800011111', 'stu0@pms.com'),
('staff1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '张工', 'staff', '13800000002', 'staff1@pms.com'),
('teacher1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '王老师', 'teacher', '13800000004', 'teacher1@pms.com'),
('student1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfJAAGMrZnFHbNi', '张同学', 'student', '13800000006', 'student1@pms.com');



-- 插入资产数据
INSERT INTO assets (id, name, type, location, purchase_date, lifespan, status, description) VALUES
('A20240001', '投影仪', '教学设备', '教学楼A101', '2023-01-15', '5年', 'normal', 'EPSON CB-X05'),
('A20240002', '空调', '设施设备', '教学楼A101', '2023-02-20', '8年', 'normal', '格力空调'),
('A20240003', '电脑', '教学设备', '教学楼B201', '2023-03-10', '4年', 'normal', 'Dell OptiPlex 7090'),
('A20240004', '投影仪', '教学设备', '教学楼B201', '2023-01-15', '5年', 'repair', 'EPSON CB-X05'),
('A20240005', '课桌椅套装', '教学设备', '教学楼C301', '2023-04-01', '10年', 'normal', '50套课桌椅');

-- 插入报修数据
INSERT INTO repairs (id, type, asset_id, location, description, submitter_id, status, submit_time, complete_time) VALUES
('R20240001', 'equipment', 'A20240004', '教学楼B201', '投影仪无法开机', 4, 'processing', '2024-01-10 09:00:00', NULL),
('R20240002', 'facility', NULL, '教学楼A101', '天花板漏水', 6, 'pending', '2024-01-12 14:30:00', NULL),
('R20240003', 'equipment', 'A20240003', '教学楼B201', '电脑蓝屏', 5, 'completed', '2024-01-08 10:20:00', '2024-01-09 15:30:00');

-- 插入维修分配数据
INSERT INTO maintenance (repair_id, maintainer_id, assign_time, expected_time, actual_time, result) VALUES
('R20240001', 2, '2024-01-10 10:00:00', '2024-01-11 17:00:00', NULL, NULL),
('R20240003', 3, '2024-01-08 11:00:00', '2024-01-09 17:00:00', '2024-01-09 15:30:00', '更换主板，已恢复正常');

-- 插入费用数据
INSERT INTO finances (type, amount, description, operator_id, create_time) VALUES
('repair', 2800.00, '更换电脑主板', 2, '2024-01-09 16:00:00'),
('maintenance', 500.00, '日常设备维护费用', 2, '2024-01-05 14:00:00'),
('purchase', 1200.00, '购买清洁用品', 3, '2024-01-03 10:00:00');

-- 插入教室数据
INSERT INTO classrooms (room_no, building, type, capacity, facilities, status) VALUES
('A101', '教学楼A', 'multimedia', 50, '投影仪,空调,电脑', 'available'),
('A102', '教学楼A', 'normal', 45, '黑板,空调', 'available'),
('B201', '教学楼B', 'multimedia', 60, '投影仪,空调,电脑,音响', 'maintenance'),
('B202', '教学楼B', 'normal', 45, '黑板,空调', 'booked'),
('C301', '教学楼C', 'multimedia', 80, '投影仪,空调,电脑,音响,演讲台', 'available');

-- 插入教室预约数据
INSERT INTO classroom_bookings (classroom_id, user_id, booking_date, start_time, end_time, purpose, status) VALUES
(1, 4, '2024-01-15', '08:00:00', '09:40:00', '高等数学课程', 'approved'),
(2, 5, '2024-01-15', '10:00:00', '11:40:00', '英语课程', 'approved'),
(4, 4, '2024-01-16', '14:00:00', '15:40:00', '物理实验课程', 'pending'),
(5, 5, '2024-01-17', '08:00:00', '09:40:00', '计算机基础课程', 'approved');

-- 插入公告数据
INSERT INTO notices (title, content, publisher_id, status) VALUES
('关于寒假期间教室使用安排的通知', '为做好寒假期间教室管理工作，现将有关事项通知如下：...', 1, 'published'),
('物业费缴纳通知', '请各位老师同学于本月底前完成物业费缴纳，逾期将收取滞纳金...', 2, 'published'),
('教学楼B维修通知', '教学楼B将于本周六进行水电维修，期间可能会影响正常使用...', 2, 'published'),
('节能减排倡议书', '为响应国家节能减排号召，请大家注意节约用电用水...', 1, 'published');