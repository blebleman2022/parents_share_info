-- K12家校学习资料共享平台 - 数据库设计
-- 数据库：PostgreSQL

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(11) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    city VARCHAR(50),
    child_grade VARCHAR(20), -- 孩子年级：小学1-6年级，初中1-3年级，高中1-3年级
    points INTEGER DEFAULT 100, -- 积分，新用户默认100
    level VARCHAR(20) DEFAULT '新手用户', -- 用户等级
    daily_downloads INTEGER DEFAULT 0, -- 当日下载次数
    last_download_date DATE, -- 最后下载日期
    last_signin_date DATE, -- 最后签到日期
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 资源表
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    uploader_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL, -- 文件大小（字节）
    file_type VARCHAR(50) NOT NULL, -- 文件类型：pdf, doc, docx, ppt, pptx, xls, xlsx, jpg, png
    grade VARCHAR(20) NOT NULL, -- 年级
    subject VARCHAR(20) NOT NULL, -- 科目
    resource_type VARCHAR(20) NOT NULL, -- 资源类型：试卷、教辅、课件、笔记、其他
    download_count INTEGER DEFAULT 0, -- 下载次数
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 下载记录表
CREATE TABLE downloads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    points_cost INTEGER DEFAULT 10, -- 消耗积分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id) -- 防止重复下载同一资源
);

-- 积分变动记录表
CREATE TABLE point_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL, -- 交易类型：register, upload, download, signin, bounty_create, bounty_reward
    points_change INTEGER NOT NULL, -- 积分变化（正数为获得，负数为消耗）
    related_resource_id INTEGER REFERENCES resources(id) ON DELETE SET NULL,
    related_bounty_id INTEGER, -- 关联悬赏ID
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 悬赏表
CREATE TABLE bounties (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    grade VARCHAR(20) NOT NULL,
    subject VARCHAR(20) NOT NULL,
    points_reward INTEGER NOT NULL, -- 悬赏积分
    status VARCHAR(20) DEFAULT 'active', -- 状态：active, completed, expired
    winner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    winning_resource_id INTEGER REFERENCES resources(id) ON DELETE SET NULL,
    expires_at TIMESTAMP NOT NULL, -- 过期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 悬赏响应表
CREATE TABLE bounty_responses (
    id SERIAL PRIMARY KEY,
    bounty_id INTEGER REFERENCES bounties(id) ON DELETE CASCADE,
    responder_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    message TEXT, -- 响应说明
    is_selected BOOLEAN DEFAULT FALSE, -- 是否被选中
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 收藏表
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id)
);

-- 举报表
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reported_resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    reported_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(20) NOT NULL, -- 举报类型：copyright, inappropriate, format_error, spam
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 状态：pending, resolved, rejected
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户行为日志表
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL, -- 行为类型：login, upload, download, search, signin
    resource_id INTEGER REFERENCES resources(id) ON DELETE SET NULL,
    details JSONB, -- 行为详情（JSON格式）
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_points ON users(points);
CREATE INDEX idx_resources_uploader ON resources(uploader_id);
CREATE INDEX idx_resources_grade_subject ON resources(grade, subject);
CREATE INDEX idx_resources_created_at ON resources(created_at);
CREATE INDEX idx_resources_download_count ON resources(download_count);
CREATE INDEX idx_downloads_user_id ON downloads(user_id);
CREATE INDEX idx_downloads_resource_id ON downloads(resource_id);
CREATE INDEX idx_point_transactions_user_id ON point_transactions(user_id);
CREATE INDEX idx_bounties_creator_id ON bounties(creator_id);
CREATE INDEX idx_bounties_status ON bounties(status);
CREATE INDEX idx_bounty_responses_bounty_id ON bounty_responses(bounty_id);
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at);

-- 插入系统配置初始数据
INSERT INTO system_configs (config_key, config_value, description) VALUES
('max_file_size', '52428800', '最大文件大小（字节），默认50MB'),
('allowed_file_types', 'pdf,doc,docx,ppt,pptx,xls,xlsx,jpg,png', '允许的文件类型'),
('daily_download_limits', '{"新手用户":5,"活跃用户":15,"资深用户":30,"专家用户":-1}', '每日下载限制'),
('point_rules', '{"register":100,"upload":20,"download":10,"signin":5,"download_reward":2}', '积分规则'),
('user_levels', '{"新手用户":[0,499],"活跃用户":[500,1999],"资深用户":[2000,4999],"专家用户":[5000,-1]}', '用户等级积分范围');

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bounties_updated_at BEFORE UPDATE ON bounties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
