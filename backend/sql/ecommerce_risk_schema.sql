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
    `priority` INT NOT NULL DEFAULT 100 COMMENT '规则优先级，数值越大优先级越高',
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
    `case_status` VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '案件状态：pending/approved/rejected',
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
    `action_type` VARCHAR(64) NOT NULL COMMENT '操作类型：create/assign/approve/reject/resolve/comment',
    `from_status` VARCHAR(32) NULL COMMENT '操作前案件状态',
    `to_status` VARCHAR(32) NULL COMMENT '操作后案件状态',
    `action_remark` TEXT NULL COMMENT '操作备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_review_logs_case_id_created_at` (`case_id`, `created_at`),
    KEY `idx_review_logs_operator_id_created_at` (`operator_id`, `created_at`),
    KEY `idx_review_logs_action_type` (`action_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审核日志表';

