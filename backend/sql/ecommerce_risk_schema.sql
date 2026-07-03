SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE DATABASE IF NOT EXISTS `ecommerce_risk_control`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `ecommerce_risk_control`;

-- ============================================
-- 表名：sys_users（后台用户表）
-- 说明：存储风控后台登录用户
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_users` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(64) NOT NULL COMMENT '登录账号',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `real_name` VARCHAR(64) NOT NULL COMMENT '用户姓名',
    `status` VARCHAR(32) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled/disabled',
    `last_login_at` DATETIME NULL COMMENT '最近登录时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sys_users_username` (`username`),
    KEY `idx_sys_users_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='后台用户表';

-- ============================================
-- 表名：sys_roles（角色表）
-- 说明：存储风控后台角色
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_roles` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_code` VARCHAR(64) NOT NULL COMMENT '角色编码',
    `role_name` VARCHAR(64) NOT NULL COMMENT '角色名称',
    `description` TEXT NULL COMMENT '角色说明',
    `status` VARCHAR(32) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled/disabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sys_roles_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- ============================================
-- 表名：sys_permissions（权限表）
-- 说明：存储菜单和接口权限点
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_permissions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `permission_code` VARCHAR(128) NOT NULL COMMENT '权限编码',
    `permission_name` VARCHAR(128) NOT NULL COMMENT '权限名称',
    `permission_type` VARCHAR(32) NOT NULL DEFAULT 'api' COMMENT '权限类型：api/menu/action',
    `description` TEXT NULL COMMENT '权限说明',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sys_permissions_code` (`permission_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- ============================================
-- 表名：sys_user_roles（用户角色关联表）
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_user_roles` (
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `role_id` BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`user_id`, `role_id`),
    CONSTRAINT `fk_sys_user_roles_user` FOREIGN KEY (`user_id`) REFERENCES `sys_users` (`id`),
    CONSTRAINT `fk_sys_user_roles_role` FOREIGN KEY (`role_id`) REFERENCES `sys_roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- ============================================
-- 表名：sys_role_permissions（角色权限关联表）
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_role_permissions` (
    `role_id` BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    `permission_id` BIGINT UNSIGNED NOT NULL COMMENT '权限ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`role_id`, `permission_id`),
    CONSTRAINT `fk_sys_role_permissions_role` FOREIGN KEY (`role_id`) REFERENCES `sys_roles` (`id`),
    CONSTRAINT `fk_sys_role_permissions_permission` FOREIGN KEY (`permission_id`) REFERENCES `sys_permissions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- ============================================
-- 表名：sys_menus（菜单表）
-- 说明：存储前端菜单与权限点映射
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_menus` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `menu_code` VARCHAR(64) NOT NULL COMMENT '菜单编码',
    `menu_name` VARCHAR(64) NOT NULL COMMENT '菜单名称',
    `route_path` VARCHAR(128) NOT NULL COMMENT '前端路由',
    `permission_code` VARCHAR(128) NULL COMMENT '展示该菜单需要的权限编码',
    `icon` VARCHAR(64) NULL COMMENT '图标',
    `sort_order` INT NOT NULL DEFAULT 100 COMMENT '排序',
    `status` VARCHAR(32) NOT NULL DEFAULT 'enabled' COMMENT '状态：enabled/disabled',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_sys_menus_menu_code` (`menu_code`),
    KEY `idx_sys_menus_status_sort` (`status`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- ============================================
-- 表名：sys_login_logs（登录日志表）
-- ============================================
CREATE TABLE IF NOT EXISTS `sys_login_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT UNSIGNED NULL COMMENT '用户ID',
    `username` VARCHAR(64) NOT NULL COMMENT '登录账号',
    `login_status` VARCHAR(32) NOT NULL COMMENT '登录状态：success/failed',
    `login_message` VARCHAR(255) NULL COMMENT '登录说明',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_sys_login_logs_username_created_at` (`username`, `created_at`),
    KEY `idx_sys_login_logs_user_id_created_at` (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录日志表';

-- ============================================
-- 表名：risk_events（风险事件表）
-- 说明：存储所有接入的业务事件原始数据
-- ============================================
CREATE TABLE IF NOT EXISTS `risk_events` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `event_type` VARCHAR(64) NOT NULL COMMENT '事件类型：order_create/order_pay/after_sale_apply/logistics_complaint',
    `source_id` VARCHAR(64) NOT NULL COMMENT '外部来源请求唯一标识，用于幂等控制',
    `user_id` VARCHAR(64) NOT NULL COMMENT '用户编号',
    `order_id` VARCHAR(64) NULL COMMENT '订单编号，部分事件可为空',
    `event_payload_json` JSON NOT NULL COMMENT '事件原始入参JSON',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_risk_events_source_id` (`source_id`),
    KEY `idx_risk_events_user_id_created_at` (`user_id`, `created_at`),
    KEY `idx_risk_events_order_id` (`order_id`),
    KEY `idx_risk_events_event_type_created_at` (`event_type`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险事件表';

-- ============================================
-- 表名：risk_assessments（风险评估表）
-- 说明：存储每次风险检查的最终评分、等级和决策结果
-- ============================================
CREATE TABLE IF NOT EXISTS `risk_assessments` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `event_id` BIGINT UNSIGNED NOT NULL COMMENT '风险事件ID，关联risk_events.id',
    `risk_score` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '风险评分，范围0到100',
    `risk_level` VARCHAR(32) NOT NULL COMMENT '风险等级：low/medium/high',
    `decision` VARCHAR(32) NOT NULL COMMENT '处理建议：pass/manual_review/reject',
    `assessment_status` VARCHAR(32) NOT NULL DEFAULT 'completed' COMMENT '评估状态：processing/completed/failed',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_risk_assessments_event_id` (`event_id`),
    KEY `idx_risk_assessments_risk_level_created_at` (`risk_level`, `created_at`),
    KEY `idx_risk_assessments_decision_created_at` (`decision`, `created_at`),
    KEY `idx_risk_assessments_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险评估表';

-- ============================================
-- 表名：feature_snapshots（特征快照表）
-- 说明：存储评估时刻的特征键值对快照
-- ============================================
CREATE TABLE IF NOT EXISTS `feature_snapshots` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `assessment_id` BIGINT UNSIGNED NOT NULL COMMENT '风险评估ID，关联risk_assessments.id',
    `feature_json` JSON NOT NULL COMMENT '特征快照JSON键值对',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_feature_snapshots_assessment_id` (`assessment_id`),
    KEY `idx_feature_snapshots_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='特征快照表';

-- ============================================
-- 表名：risk_rules（风险规则表）
-- 说明：存储风控规则配置
-- ============================================
CREATE TABLE IF NOT EXISTS `risk_rules` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `rule_code` VARCHAR(64) NOT NULL COMMENT '规则编码',
    `rule_name` VARCHAR(128) NOT NULL COMMENT '规则名称',
    `rule_status` VARCHAR(32) NOT NULL DEFAULT 'enabled' COMMENT '规则状态：enabled/disabled',
    `priority` INT NOT NULL DEFAULT 100 COMMENT '规则优先级，数值越小优先级越高',
    `score` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '命中分值',
    `condition_json` JSON NOT NULL COMMENT '规则条件JSON',
    `description` TEXT NULL COMMENT '规则描述',
    `hit_count` INT NOT NULL DEFAULT 0 COMMENT '规则累计命中次数，便于列表展示和看板统计',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_risk_rules_rule_code` (`rule_code`),
    KEY `idx_risk_rules_status_priority` (`rule_status`, `priority`),
    KEY `idx_risk_rules_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险规则表';

-- ============================================
-- 表名：rule_hits（规则命中表）
-- 说明：存储每次风险评估命中的规则记录
-- ============================================
CREATE TABLE IF NOT EXISTS `rule_hits` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `assessment_id` BIGINT UNSIGNED NOT NULL COMMENT '风险评估ID，关联risk_assessments.id',
    `rule_id` BIGINT UNSIGNED NOT NULL COMMENT '风险规则ID，关联risk_rules.id',
    `hit_score` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '命中分值',
    `hit_message` TEXT NULL COMMENT '命中描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_rule_hits_assessment_id` (`assessment_id`),
    KEY `idx_rule_hits_rule_id_created_at` (`rule_id`, `created_at`),
    KEY `idx_rule_hits_assessment_id_rule_id` (`assessment_id`, `rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规则命中表';

-- ============================================
-- 表名：risk_cases（风险案件表）
-- 说明：存储需要人工审核或拒绝处置的风险案件
-- ============================================
CREATE TABLE IF NOT EXISTS `risk_cases` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `assessment_id` BIGINT UNSIGNED NOT NULL COMMENT '风险评估ID，关联risk_assessments.id',
    `user_id` VARCHAR(64) NOT NULL COMMENT '用户编号',
    `order_id` VARCHAR(64) NULL COMMENT '订单编号',
    `case_status` VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '案件状态：pending/reviewing/approved/rejected',
    `reviewer_id` VARCHAR(64) NULL COMMENT '审核人ID',
    `review_result` TEXT NULL COMMENT '审核结论',
    `review_remark` TEXT NULL COMMENT '审核备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_risk_cases_assessment_id` (`assessment_id`),
    KEY `idx_risk_cases_status_created_at` (`case_status`, `created_at`),
    KEY `idx_risk_cases_user_id_created_at` (`user_id`, `created_at`),
    KEY `idx_risk_cases_order_id` (`order_id`),
    KEY `idx_risk_cases_reviewer_id_status` (`reviewer_id`, `case_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险案件表';

-- ============================================
-- 表名：blacklists（黑名单表）
-- 说明：存储风控黑名单数据
-- ============================================
CREATE TABLE IF NOT EXISTS `blacklists` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `blacklist_type` VARCHAR(64) NOT NULL COMMENT '黑名单类型：user_id/phone/address/device_id/ip/order_id',
    `blacklist_value` VARCHAR(128) NOT NULL COMMENT '黑名单命中值',
    `remark` TEXT NULL COMMENT '备注',
    `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '状态：active/inactive/deleted',
    `created_by` VARCHAR(64) NULL COMMENT '创建人ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_blacklists_type_value` (`blacklist_type`, `blacklist_value`),
    KEY `idx_blacklists_status_type` (`status`, `blacklist_type`),
    KEY `idx_blacklists_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='黑名单表';

-- ============================================
-- 表名：review_logs（审核日志表）
-- 说明：存储案件审核操作日志和状态流转记录
-- ============================================
CREATE TABLE IF NOT EXISTS `review_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `case_id` BIGINT UNSIGNED NOT NULL COMMENT '风险案件ID，关联risk_cases.id',
    `operator_id` VARCHAR(64) NOT NULL COMMENT '操作人ID',
    `action_type` VARCHAR(64) NOT NULL COMMENT '操作类型：create/assign/start_review/approve/reject/resolve/comment',
    `from_status` VARCHAR(32) NULL COMMENT '操作前案件状态',
    `to_status` VARCHAR(32) NULL COMMENT '操作后案件状态',
    `action_remark` TEXT NULL COMMENT '操作备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_review_logs_case_id_created_at` (`case_id`, `created_at`),
    KEY `idx_review_logs_operator_id_created_at` (`operator_id`, `created_at`),
    KEY `idx_review_logs_action_type` (`action_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审核日志表';

-- ============================================
-- 初始化后台角色、默认用户、权限和菜单
-- 默认用户密码：
-- risk_admin / 123456
-- risk_auditor / 123456
-- data_viewer / 123456
-- ============================================
INSERT IGNORE INTO `sys_roles` (`role_code`, `role_name`, `description`, `status`) VALUES
('risk_admin', '风控管理员', '维护规则、维护黑名单、查看统计看板、管理后台用户权限', 'enabled'),
('risk_auditor', '风控审核员', '查看风险结果、审核案件、填写处理结论', 'enabled'),
('data_viewer', '数据查看人', '查看用户画像、历史风险记录和命中统计', 'enabled');

INSERT IGNORE INTO `sys_users` (`username`, `password_hash`, `real_name`, `status`) VALUES
('risk_admin', 'pbkdf2_sha256$100000$ecommerce-risk-default$748ed10144a8eb6b367637cc1ddd555d360c17f6294ac6c0db592d341d05b306', '风控管理员', 'enabled'),
('risk_auditor', 'pbkdf2_sha256$100000$ecommerce-risk-default$748ed10144a8eb6b367637cc1ddd555d360c17f6294ac6c0db592d341d05b306', '风控审核员', 'enabled'),
('data_viewer', 'pbkdf2_sha256$100000$ecommerce-risk-default$748ed10144a8eb6b367637cc1ddd555d360c17f6294ac6c0db592d341d05b306', '数据查看人', 'enabled');

INSERT IGNORE INTO `sys_user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id FROM `sys_users` u JOIN `sys_roles` r ON r.role_code = 'risk_admin' WHERE u.username = 'risk_admin';
INSERT IGNORE INTO `sys_user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id FROM `sys_users` u JOIN `sys_roles` r ON r.role_code = 'risk_auditor' WHERE u.username = 'risk_auditor';
INSERT IGNORE INTO `sys_user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id FROM `sys_users` u JOIN `sys_roles` r ON r.role_code = 'data_viewer' WHERE u.username = 'data_viewer';

INSERT IGNORE INTO `sys_permissions` (`permission_code`, `permission_name`, `permission_type`, `description`) VALUES
('risk:check', '执行风险检查', 'api', '允许提交风险检查请求'),
('risk:assessment:read', '查看风险结果', 'api', '允许查看风险评估详情'),
('rule:read', '查看规则', 'api', '允许查看规则列表和规则详情'),
('rule:write', '维护规则', 'api', '允许新增、编辑、启停和删除规则'),
('rule:ai', 'AI辅助规则', 'api', '允许使用AI辅助生成、解释和校验规则'),
('case:read', '查看案件', 'api', '允许查看案件列表和案件详情'),
('case:review', '审核案件', 'api', '允许提交案件审核结论'),
('blacklist:read', '查看黑名单', 'api', '允许查看黑名单列表'),
('blacklist:write', '维护黑名单', 'api', '允许新增、删除和导入黑名单'),
('profile:read', '查看用户画像', 'api', '允许查看用户画像和历史风险记录'),
('dashboard:read', '查看运营看板', 'api', '允许查看运营看板和命中统计'),
('system:user:read', '查看后台用户', 'api', '允许查看后台用户'),
('system:user:write', '维护后台用户', 'api', '允许新增用户、启停用户和重置密码'),
('system:role:read', '查看角色', 'api', '允许查看角色'),
('system:role:write', '维护角色', 'api', '允许新增角色'),
('system:permission:read', '查看权限', 'api', '允许查看权限点');

INSERT IGNORE INTO `sys_menus` (`menu_code`, `menu_name`, `route_path`, `permission_code`, `icon`, `sort_order`, `status`) VALUES
('risk_check', '风险检查', '/risk-check', 'risk:check', 'Search', 10, 'enabled'),
('rules', '规则管理', '/rules', 'rule:write', 'Setting', 20, 'enabled'),
('ai_rules', 'AI 辅助规则', '/ai-rules', 'rule:ai', 'MagicStick', 30, 'enabled'),
('cases', '案件管理', '/cases', 'case:read', 'Tickets', 40, 'enabled'),
('blacklists', '黑名单管理', '/blacklists', 'blacklist:read', 'CircleClose', 50, 'enabled'),
('profile', '用户画像', '/users/profile', 'profile:read', 'User', 60, 'enabled'),
('dashboard', '运营看板', '/dashboard', 'dashboard:read', 'DataAnalysis', 70, 'enabled'),
('system_users', '用户权限', '/system/users', 'system:user:read', 'Lock', 80, 'enabled');

INSERT IGNORE INTO `sys_role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id FROM `sys_roles` r JOIN `sys_permissions` p ON 1 = 1 WHERE r.role_code = 'risk_admin';
INSERT IGNORE INTO `sys_role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id FROM `sys_roles` r JOIN `sys_permissions` p ON p.permission_code IN ('risk:check', 'risk:assessment:read', 'case:read', 'case:review', 'profile:read')
WHERE r.role_code = 'risk_auditor';
INSERT IGNORE INTO `sys_role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id FROM `sys_roles` r JOIN `sys_permissions` p ON p.permission_code IN ('risk:assessment:read', 'profile:read', 'dashboard:read')
WHERE r.role_code = 'data_viewer';

-- ============================================
-- 初始化风险规则数据
-- ============================================
INSERT INTO `risk_rules`
(`rule_code`, `rule_name`, `rule_status`, `priority`, `score`, `condition_json`, `description`)
VALUES
('USER_BLACKLIST', '用户命中黑名单', 'enabled', 1, 100.00, '{"operator":"=","feature":"is_user_blacklisted","value":true}', '用户编号命中有效黑名单，建议直接拒绝或人工复核'),
('ORDER_BLACKLIST', '订单命中黑名单', 'enabled', 2, 100.00, '{"operator":"=","feature":"is_order_blacklisted","value":true}', '订单编号命中有效黑名单，建议直接拒绝'),
('PHONE_MULTI_USER', '手机号关联用户过多', 'enabled', 10, 35.00, '{"operator":">","feature":"phone_related_user_count","value":3}', '同一手机号关联多个用户，存在账号团伙风险'),
('DEVICE_MULTI_USER', '设备关联用户过多', 'enabled', 11, 35.00, '{"operator":">","feature":"device_related_user_count","value":5}', '同一设备关联多个用户，存在批量注册或刷单风险'),
('IP_HIGH_RISK', 'IP命中高风险地区', 'enabled', 12, 30.00, '{"operator":"=","feature":"is_ip_high_risk_area","value":true}', '请求IP归属高风险地区'),
('USER_REGISTER_NEW_HIGH_AMOUNT', '新用户高额订单', 'enabled', 20, 35.00, '{"operator":"and","conditions":[{"feature":"user_register_days","operator":"<","value":7},{"feature":"order_amount","operator":">","value":3000}]}', '注册7天内的新用户发起高额订单'),
('USER_REFUND_RATE_HIGH', '用户退款率过高', 'enabled', 21, 25.00, '{"operator":">","feature":"user_refund_rate_90d","value":0.3}', '用户近90天退款率超过30%'),
('USER_COMPLAINT_HIGH', '用户投诉次数过多', 'enabled', 22, 20.00, '{"operator":">","feature":"user_complaint_count_90d","value":3}', '用户近90天投诉次数过多'),
('USER_HIGH_RISK_HISTORY', '用户历史高风险次数过多', 'enabled', 23, 30.00, '{"operator":">","feature":"user_high_risk_count_180d","value":2}', '用户历史多次被判定为高风险'),
('USER_REJECT_HISTORY', '用户历史拒绝次数过多', 'enabled', 24, 30.00, '{"operator":">","feature":"user_reject_count_180d","value":1}', '用户历史存在多次拒绝处置'),
('ORDER_AMOUNT_HIGH', '订单金额过高', 'enabled', 30, 25.00, '{"operator":">","feature":"order_amount","value":5000}', '订单金额超过高额阈值'),
('ORDER_ITEMS_HIGH', '订单商品数量异常', 'enabled', 31, 15.00, '{"operator":">","feature":"order_item_count","value":20}', '单笔订单商品数量异常偏高'),
('COUPON_ABUSE', '优惠券使用异常', 'enabled', 32, 20.00, '{"operator":"and","conditions":[{"feature":"is_coupon_used","operator":"=","value":true},{"feature":"coupon_discount_rate","operator":">","value":0.5}]}', '订单使用高折扣优惠券，存在薅羊毛风险'),
('FIRST_ORDER_HIGH_AMOUNT', '首单金额异常偏高', 'enabled', 33, 20.00, '{"operator":"and","conditions":[{"feature":"is_first_order","operator":"=","value":true},{"feature":"order_amount","operator":">","value":2000}]}', '用户首单金额异常偏高'),
('USER_ORDER_1H_HIGH', '用户短时间下单频繁', 'enabled', 34, 25.00, '{"operator":">","feature":"user_order_count_1h","value":5}', '同一用户1小时内下单次数过多'),
('USER_CANCEL_7D_HIGH', '用户近期取消订单过多', 'enabled', 35, 15.00, '{"operator":">","feature":"user_cancel_count_7d","value":3}', '用户近7天取消订单次数过多'),
('AFTER_SALE_7D_HIGH', '用户近期售后申请过多', 'enabled', 36, 20.00, '{"operator":">","feature":"user_after_sale_count_7d","value":2}', '用户近7天售后申请次数过多'),
('ADDRESS_USER_COUNT_HIGH', '地址关联用户过多', 'enabled', 40, 25.00, '{"operator":">","feature":"address_related_user_count","value":4}', '同一收货地址关联多个用户'),
('ADDRESS_ORDER_1D_HIGH', '地址近期订单过多', 'enabled', 41, 20.00, '{"operator":">","feature":"address_order_count_1d","value":10}', '同一地址1天内订单数量过多'),
('ADDRESS_IP_MISMATCH', '地址与IP所在地不一致', 'enabled', 42, 10.00, '{"operator":"=","feature":"is_address_ip_mismatch","value":true}', '收货地址与请求IP所在地不一致'),
('ADDRESS_HIGH_RISK_AREA', '收货地址命中高风险地区', 'enabled', 43, 30.00, '{"operator":"=","feature":"is_address_high_risk_area","value":true}', '收货地址属于高风险地区'),
('DEVICE_ORDER_1H_HIGH', '设备短时间下单频繁', 'enabled', 50, 25.00, '{"operator":">","feature":"device_order_count_1h","value":8}', '同一设备1小时内下单次数过多'),
('IP_ORDER_1H_HIGH', 'IP短时间下单频繁', 'enabled', 51, 25.00, '{"operator":">","feature":"ip_order_count_1h","value":10}', '同一IP 1小时内下单次数过多'),
('LOGISTICS_COMPLAINT_REPEAT', '物流投诉重复发生', 'enabled', 60, 20.00, '{"operator":">","feature":"logistics_complaint_count_30d","value":2}', '用户近30天物流投诉次数过多'),
('PAYMENT_METHOD_RISK', '支付方式风险较高', 'enabled', 61, 10.00, '{"operator":"in","feature":"payment_method","value":["virtual_card","unknown"]}', '支付方式属于高风险或未知类型');
