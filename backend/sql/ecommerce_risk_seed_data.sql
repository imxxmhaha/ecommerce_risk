SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

USE `ecommerce_risk_control`;

-- ============================================================
-- 电商风控系统业务演示数据
-- 说明：
-- 1. 本脚本依赖 ecommerce_risk_schema.sql 中的 8 张核心表和初始化规则。
-- 2. 数据覆盖低/中/高风险、规则命中、自动建案、人工审核、黑名单、画像和看板。
-- 3. 为便于重复执行，脚本会先清理本脚本使用的演示 ID 和黑名单值。
-- ============================================================

START TRANSACTION;

-- 清理演示数据
DELETE FROM `review_logs` WHERE `case_id` BETWEEN 9001 AND 9006;
DELETE FROM `risk_cases` WHERE `id` BETWEEN 9001 AND 9006;
DELETE FROM `rule_hits` WHERE `assessment_id` BETWEEN 8001 AND 8012;
DELETE FROM `feature_snapshots` WHERE `assessment_id` BETWEEN 8001 AND 8012;
DELETE FROM `risk_assessments` WHERE `id` BETWEEN 8001 AND 8012;
DELETE FROM `risk_events` WHERE `id` BETWEEN 7001 AND 7012;
DELETE FROM `blacklists`
WHERE (`blacklist_type`, `blacklist_value`) IN (
    ('user_id', 'U90001'),
    ('order_id', 'O90001'),
    ('phone', '13900000001'),
    ('device_id', 'D-RISK-001'),
    ('ip', '10.10.10.10'),
    ('address', '高风险地区A-共享仓')
);

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
-- 支付类（低风险，priority 20-29）
('PAYMENT_METHOD_RISK', '支付方式风险较高', 'enabled', 29, 25.00, '{"operator":"in","feature":"payment_method","value":["virtual_card","unknown"]}', '支付方式属于高风险或未知类型'),
-- 用户行为-低风险（priority 30-39）
('LOGISTICS_COMPLAINT_REPEAT', '物流投诉重复发生', 'enabled', 36, 30.00, '{"operator":">","feature":"logistics_complaint_count_30d","value":2}', '用户近30天物流投诉次数过多'),
('USER_CANCEL_7D_HIGH', '用户近期取消订单过多', 'enabled', 38, 35.00, '{"operator":">","feature":"user_cancel_count_7d","value":3}', '用户近7天取消订单次数过多'),
('AFTER_SALE_7D_HIGH', '用户近期售后申请过多', 'enabled', 37, 35.00, '{"operator":">","feature":"user_after_sale_count_7d","value":2}', '用户近7天售后申请次数过多'),
('USER_COMPLAINT_HIGH', '用户投诉次数过多', 'enabled', 39, 40.00, '{"operator":">","feature":"user_complaint_count_90d","value":3}', '用户近90天投诉次数过多'),
-- 订单类（中低风险，priority 40-49）
('ORDER_ITEMS_HIGH', '订单商品数量异常', 'enabled', 46, 35.00, '{"operator":">","feature":"order_item_count","value":20}', '单笔订单商品数量异常偏高'),
('FIRST_ORDER_HIGH_AMOUNT', '首单金额异常偏高', 'enabled', 47, 45.00, '{"operator":"and","conditions":[{"feature":"is_first_order","operator":"=","value":true},{"feature":"order_amount","operator":">","value":2000}]}', '用户首单金额异常偏高'),
('COUPON_ABUSE', '优惠券使用异常', 'enabled', 48, 50.00, '{"operator":"and","conditions":[{"feature":"is_coupon_used","operator":"=","value":true},{"feature":"coupon_discount_rate","operator":">","value":0.5}]}', '订单使用高折扣优惠券，存在薅羊毛风险'),
('ORDER_AMOUNT_HIGH', '订单金额过高', 'enabled', 49, 55.00, '{"operator":">","feature":"order_amount","value":5000}', '订单金额超过高额阈值'),
-- 地址类（中风险，priority 50-59）
('ADDRESS_IP_MISMATCH', '地址与IP所在地不一致', 'enabled', 56, 45.00, '{"operator":"=","feature":"is_address_ip_mismatch","value":true}', '收货地址与请求IP所在地不一致'),
('ADDRESS_ORDER_1D_HIGH', '地址近期订单过多', 'enabled', 57, 50.00, '{"operator":">","feature":"address_order_count_1d","value":10}', '同一地址1天内订单数量过多'),
('ADDRESS_USER_COUNT_HIGH', '地址关联用户过多', 'enabled', 58, 55.00, '{"operator":">","feature":"address_related_user_count","value":4}', '同一收货地址关联多个用户'),
('ADDRESS_HIGH_RISK_AREA', '收货地址命中高风险地区', 'enabled', 59, 60.00, '{"operator":"=","feature":"is_address_high_risk_area","value":true}', '收货地址属于高风险地区'),
-- 设备/IP/手机类（中高风险，priority 60-69）
('IP_ORDER_1H_HIGH', 'IP短时间下单频繁', 'enabled', 65, 50.00, '{"operator":">","feature":"ip_order_count_1h","value":10}', '同一IP 1小时内下单次数过多'),
('DEVICE_ORDER_1H_HIGH', '设备短时间下单频繁', 'enabled', 66, 55.00, '{"operator":">","feature":"device_order_count_1h","value":8}', '同一设备1小时内下单次数过多'),
('IP_HIGH_RISK', 'IP命中高风险地区', 'enabled', 67, 55.00, '{"operator":"=","feature":"is_ip_high_risk_area","value":true}', '请求IP归属高风险地区'),
('PHONE_MULTI_USER', '手机号关联用户过多', 'enabled', 68, 60.00, '{"operator":">","feature":"phone_related_user_count","value":3}', '同一手机号关联多个用户，存在账号团伙风险'),
('DEVICE_MULTI_USER', '设备关联用户过多', 'enabled', 69, 65.00, '{"operator":">","feature":"device_related_user_count","value":5}', '同一设备关联多个用户，存在批量注册或刷单风险'),
-- 用户行为类（高风险，priority 70-79）
('USER_ORDER_1H_HIGH', '用户短时间下单频繁', 'enabled', 75, 65.00, '{"operator":">","feature":"user_order_count_1h","value":5}', '同一用户1小时内下单次数过多'),
('USER_REGISTER_NEW_HIGH_AMOUNT', '新用户高额订单', 'enabled', 76, 70.00, '{"operator":"and","conditions":[{"feature":"user_register_days","operator":"<","value":7},{"feature":"order_amount","operator":">","value":3000}]}', '注册7天内的新用户发起高额订单'),
('USER_REFUND_RATE_HIGH', '用户退款率过高', 'enabled', 77, 75.00, '{"operator":">","feature":"user_refund_rate_90d","value":0.3}', '用户近90天退款率超过30%'),
('USER_REJECT_HISTORY', '用户历史拒绝次数过多', 'enabled', 78, 80.00, '{"operator":">","feature":"user_reject_count_180d","value":1}', '用户历史存在多次拒绝处置'),
('USER_HIGH_RISK_HISTORY', '用户历史高风险次数过多', 'enabled', 79, 85.00, '{"operator":">","feature":"user_high_risk_count_180d","value":2}', '用户历史多次被判定为高风险'),
-- 黑名单类（最严重，priority 90-99，score 95-100）
('ORDER_BLACKLIST', '订单命中黑名单', 'enabled', 98, 95.00, '{"operator":"=","feature":"is_order_blacklisted","value":true}', '订单编号命中有效黑名单，建议直接拒绝'),
('USER_BLACKLIST', '用户命中黑名单', 'enabled', 99, 100.00, '{"operator":"=","feature":"is_user_blacklisted","value":true}', '用户编号命中有效黑名单，建议直接拒绝或人工复核');



-- ============================================================
-- 黑名单数据
-- ============================================================
INSERT INTO `blacklists`
(`id`, `blacklist_type`, `blacklist_value`, `remark`, `status`, `created_by`, `created_at`, `updated_at`)
VALUES
(6001, 'user_id', 'U90001', '历史多次拒付和异常售后，加入用户黑名单', 'active', 'admin', '2026-07-01 09:00:00', '2026-07-01 09:00:00'),
(6002, 'order_id', 'O90001', '已确认异常订单，禁止继续交易', 'active', 'admin', '2026-07-01 09:05:00', '2026-07-01 09:05:00'),
(6003, 'phone', '13900000001', '手机号关联多个异常账号', 'active', 'admin', '2026-07-01 09:10:00', '2026-07-01 09:10:00'),
(6004, 'device_id', 'D-RISK-001', '设备关联批量注册账号', 'active', 'admin', '2026-07-01 09:15:00', '2026-07-01 09:15:00'),
(6005, 'ip', '10.10.10.10', '高风险代理 IP', 'active', 'admin', '2026-07-01 09:20:00', '2026-07-01 09:20:00'),
(6006, 'address', '高风险地区A-共享仓', '同一地址关联多个风险用户', 'active', 'admin', '2026-07-01 09:25:00', '2026-07-01 09:25:00');

-- ============================================================
-- 风险事件数据
-- ============================================================
INSERT INTO `risk_events`
(`id`, `event_type`, `source_id`, `user_id`, `order_id`, `event_payload_json`, `created_at`)
VALUES
(7001, 'order_create', 'DEMO-REQ-7001', 'U10001', 'O10001',
 JSON_OBJECT('order_amount', 5200, 'order_item_count', 25, 'payment_method', 'virtual_card', 'phone', '13800000001', 'device_id', 'D10001', 'ip', '10.0.0.1', 'address', '上海市浦东新区', 'user_register_days', 3, 'is_coupon_used', true, 'coupon_discount_rate', 0.60),
 '2026-07-01 10:00:00'),
(7002, 'order_pay', 'DEMO-REQ-7002', 'U10002', 'O10002',
 JSON_OBJECT('order_amount', 268, 'order_item_count', 2, 'payment_method', 'wechat_pay', 'phone', '13800000002', 'device_id', 'D10002', 'ip', '10.0.0.2', 'address', '北京市朝阳区', 'user_register_days', 380, 'is_coupon_used', false, 'coupon_discount_rate', 0),
 '2026-07-01 10:08:00'),
(7003, 'after_sale_apply', 'DEMO-REQ-7003', 'U10003', 'O10003',
 JSON_OBJECT('order_amount', 899, 'order_item_count', 1, 'payment_method', 'alipay', 'phone', '13800000003', 'device_id', 'D10003', 'ip', '10.0.0.3', 'address', '杭州市西湖区', 'user_register_days', 120, 'user_after_sale_count_7d', 3),
 '2026-07-01 11:20:00'),
(7004, 'logistics_complaint', 'DEMO-REQ-7004', 'U10004', 'O10004',
 JSON_OBJECT('order_amount', 1299, 'order_item_count', 1, 'payment_method', 'wechat_pay', 'phone', '13800000004', 'device_id', 'D10004', 'ip', '10.0.0.4', 'address', '广州市天河区', 'user_register_days', 60, 'logistics_complaint_count_30d', 3),
 '2026-07-01 12:10:00'),
(7005, 'order_create', 'DEMO-REQ-7005', 'U90001', 'O90001',
 JSON_OBJECT('order_amount', 7600, 'order_item_count', 3, 'payment_method', 'unknown', 'phone', '13900000001', 'device_id', 'D-RISK-001', 'ip', '10.10.10.10', 'address', '高风险地区A-共享仓', 'user_register_days', 2, 'is_coupon_used', true, 'coupon_discount_rate', 0.55),
 '2026-07-02 09:35:00'),
(7006, 'order_pay', 'DEMO-REQ-7006', 'U10005', 'O10005',
 JSON_OBJECT('order_amount', 3200, 'order_item_count', 5, 'payment_method', 'credit_card', 'phone', '13800000005', 'device_id', 'D10005', 'ip', '10.0.0.5', 'address', '深圳市南山区', 'user_register_days', 5, 'is_first_order', true),
 '2026-07-02 10:05:00'),
(7007, 'order_create', 'DEMO-REQ-7007', 'U10006', 'O10006',
 JSON_OBJECT('order_amount', 460, 'order_item_count', 3, 'payment_method', 'wechat_pay', 'phone', '13800000006', 'device_id', 'D10006', 'ip', '10.0.0.6', 'address', '成都市高新区', 'user_register_days', 240),
 '2026-07-02 14:20:00'),
(7008, 'order_create', 'DEMO-REQ-7008', 'U10007', 'O10007',
 JSON_OBJECT('order_amount', 1800, 'order_item_count', 2, 'payment_method', 'wechat_pay', 'phone', '13800000007', 'device_id', 'D10007', 'ip', '10.0.0.7', 'address', '高风险地区A-共享仓', 'user_register_days', 30, 'address_related_user_count', 5, 'address_order_count_1d', 12, 'is_address_ip_mismatch', true),
 '2026-07-02 16:45:00'),
(7009, 'order_pay', 'DEMO-REQ-7009', 'U10008', 'O10008',
 JSON_OBJECT('order_amount', 9888, 'order_item_count', 1, 'payment_method', 'bank_card', 'phone', '13800000008', 'device_id', 'D10008', 'ip', '10.0.0.8', 'address', '南京市建邺区', 'user_register_days', 500),
 '2026-07-03 09:10:00'),
(7010, 'after_sale_apply', 'DEMO-REQ-7010', 'U10001', 'O10009',
 JSON_OBJECT('order_amount', 399, 'order_item_count', 1, 'payment_method', 'wechat_pay', 'phone', '13800000001', 'device_id', 'D10001', 'ip', '10.0.0.1', 'address', '上海市浦东新区', 'user_register_days', 5, 'user_after_sale_count_7d', 4, 'user_refund_rate_90d', 0.35),
 '2026-07-03 10:30:00'),
(7011, 'logistics_complaint', 'DEMO-REQ-7011', 'U10009', 'O10010',
 JSON_OBJECT('order_amount', 79, 'order_item_count', 1, 'payment_method', 'wechat_pay', 'phone', '13800000009', 'device_id', 'D10009', 'ip', '10.0.0.9', 'address', '武汉市洪山区', 'user_register_days', 100, 'logistics_complaint_count_30d', 1),
 '2026-07-03 11:45:00'),
(7012, 'order_create', 'DEMO-REQ-7012', 'U10010', 'O10011',
 JSON_OBJECT('order_amount', 2100, 'order_item_count', 8, 'payment_method', 'unknown', 'phone', '13800000010', 'device_id', 'D10010', 'ip', '10.0.0.10', 'address', '重庆市渝中区', 'user_register_days', 15, 'user_order_count_1h', 6),
 '2026-07-03 13:05:00');

-- ============================================================
-- 风险评估数据
-- ============================================================
INSERT INTO `risk_assessments`
(`id`, `event_id`, `risk_score`, `risk_level`, `decision`, `assessment_status`, `created_at`)
VALUES
(8001, 7001, 70.00, 'medium', 'manual_review', 'completed', '2026-07-01 10:00:03'),
(8002, 7002, 0.00, 'low', 'pass', 'completed', '2026-07-01 10:08:02'),
(8003, 7003, 35.00, 'medium', 'manual_review', 'completed', '2026-07-01 11:20:04'),
(8004, 7004, 30.00, 'medium', 'manual_review', 'completed', '2026-07-01 12:10:03'),
(8005, 7005, 100.00, 'high', 'reject', 'completed', '2026-07-02 09:35:05'),
(8006, 7006, 70.00, 'medium', 'manual_review', 'completed', '2026-07-02 10:05:04'),
(8007, 7007, 0.00, 'low', 'pass', 'completed', '2026-07-02 14:20:02'),
(8008, 7008, 60.00, 'medium', 'manual_review', 'completed', '2026-07-02 16:45:03'),
(8009, 7009, 55.00, 'medium', 'manual_review', 'completed', '2026-07-03 09:10:03'),
(8010, 7010, 75.00, 'high', 'manual_review', 'completed', '2026-07-03 10:30:04'),
(8011, 7011, 0.00, 'low', 'pass', 'completed', '2026-07-03 11:45:02'),
(8012, 7012, 65.00, 'medium', 'manual_review', 'completed', '2026-07-03 13:05:04');

-- ============================================================
-- 特征快照数据
-- ============================================================
INSERT INTO `feature_snapshots`
(`id`, `assessment_id`, `feature_json`, `created_at`)
VALUES
(8101, 8001, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 3, 'user_refund_rate_90d', 0, 'user_complaint_count_90d', 0, 'user_high_risk_count_180d', 0, 'user_reject_count_180d', 0, 'order_amount', 5200, 'order_item_count', 25, 'is_coupon_used', true, 'coupon_discount_rate', 0.60, 'is_first_order', true, 'user_order_count_1h', 1, 'user_cancel_count_7d', 0, 'user_after_sale_count_7d', 0, 'address_related_user_count', 1, 'address_order_count_1d', 0, 'is_address_ip_mismatch', false, 'is_address_high_risk_area', false, 'device_order_count_1h', 1, 'ip_order_count_1h', 1, 'logistics_complaint_count_30d', 0, 'payment_method', 'virtual_card'), '2026-07-01 10:00:03'),
(8102, 8002, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 380, 'user_refund_rate_90d', 0, 'user_complaint_count_90d', 0, 'user_high_risk_count_180d', 0, 'user_reject_count_180d', 0, 'order_amount', 268, 'order_item_count', 2, 'is_coupon_used', false, 'coupon_discount_rate', 0, 'is_first_order', false, 'user_order_count_1h', 1, 'user_cancel_count_7d', 0, 'user_after_sale_count_7d', 0, 'address_related_user_count', 1, 'address_order_count_1d', 0, 'is_address_ip_mismatch', false, 'is_address_high_risk_area', false, 'device_order_count_1h', 1, 'ip_order_count_1h', 1, 'logistics_complaint_count_30d', 0, 'payment_method', 'wechat_pay'), '2026-07-01 10:08:02'),
(8103, 8003, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 120, 'user_refund_rate_90d', 0.12, 'user_complaint_count_90d', 1, 'user_high_risk_count_180d', 0, 'user_reject_count_180d', 0, 'order_amount', 899, 'order_item_count', 1, 'is_coupon_used', false, 'coupon_discount_rate', 0, 'is_first_order', false, 'user_order_count_1h', 1, 'user_cancel_count_7d', 0, 'user_after_sale_count_7d', 3, 'address_related_user_count', 1, 'address_order_count_1d', 0, 'is_address_ip_mismatch', false, 'is_address_high_risk_area', false, 'device_order_count_1h', 1, 'ip_order_count_1h', 1, 'logistics_complaint_count_30d', 0, 'payment_method', 'alipay'), '2026-07-01 11:20:04'),
(8104, 8004, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 60, 'user_refund_rate_90d', 0, 'user_complaint_count_90d', 0, 'user_high_risk_count_180d', 0, 'user_reject_count_180d', 0, 'order_amount', 1299, 'order_item_count', 1, 'is_coupon_used', false, 'coupon_discount_rate', 0, 'is_first_order', false, 'user_order_count_1h', 1, 'user_cancel_count_7d', 0, 'user_after_sale_count_7d', 0, 'address_related_user_count', 1, 'address_order_count_1d', 0, 'is_address_ip_mismatch', false, 'is_address_high_risk_area', false, 'device_order_count_1h', 1, 'ip_order_count_1h', 1, 'logistics_complaint_count_30d', 3, 'payment_method', 'wechat_pay'), '2026-07-01 12:10:03'),
(8105, 8005, JSON_OBJECT('is_user_blacklisted', true, 'is_order_blacklisted', true, 'phone_related_user_count', 6, 'device_related_user_count', 8, 'is_ip_high_risk_area', true, 'user_register_days', 2, 'user_refund_rate_90d', 0.45, 'user_complaint_count_90d', 5, 'user_high_risk_count_180d', 3, 'user_reject_count_180d', 2, 'order_amount', 7600, 'order_item_count', 3, 'is_coupon_used', true, 'coupon_discount_rate', 0.55, 'is_first_order', false, 'user_order_count_1h', 8, 'user_cancel_count_7d', 4, 'user_after_sale_count_7d', 3, 'address_related_user_count', 8, 'address_order_count_1d', 16, 'is_address_ip_mismatch', true, 'is_address_high_risk_area', true, 'device_order_count_1h', 12, 'ip_order_count_1h', 18, 'logistics_complaint_count_30d', 3, 'payment_method', 'unknown'), '2026-07-02 09:35:05'),
(8106, 8006, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 5, 'user_refund_rate_90d', 0, 'user_complaint_count_90d', 0, 'user_high_risk_count_180d', 0, 'user_reject_count_180d', 0, 'order_amount', 3200, 'order_item_count', 5, 'is_coupon_used', false, 'coupon_discount_rate', 0, 'is_first_order', true, 'user_order_count_1h', 1, 'user_cancel_count_7d', 0, 'user_after_sale_count_7d', 0, 'address_related_user_count', 1, 'address_order_count_1d', 0, 'is_address_ip_mismatch', false, 'is_address_high_risk_area', false, 'device_order_count_1h', 1, 'ip_order_count_1h', 1, 'logistics_complaint_count_30d', 0, 'payment_method', 'credit_card'), '2026-07-02 10:05:04'),
(8107, 8007, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 240, 'order_amount', 460, 'order_item_count', 3, 'payment_method', 'wechat_pay'), '2026-07-02 14:20:02'),
(8108, 8008, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'phone_related_user_count', 1, 'device_related_user_count', 1, 'is_ip_high_risk_area', false, 'user_register_days', 30, 'order_amount', 1800, 'order_item_count', 2, 'is_coupon_used', false, 'coupon_discount_rate', 0, 'is_first_order', false, 'address_related_user_count', 5, 'address_order_count_1d', 12, 'is_address_ip_mismatch', true, 'is_address_high_risk_area', true, 'payment_method', 'wechat_pay'), '2026-07-02 16:45:03'),
(8109, 8009, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'user_register_days', 500, 'order_amount', 9888, 'order_item_count', 1, 'payment_method', 'bank_card'), '2026-07-03 09:10:03'),
(8110, 8010, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'user_register_days', 5, 'user_refund_rate_90d', 0.35, 'user_after_sale_count_7d', 4, 'order_amount', 399, 'order_item_count', 1, 'payment_method', 'wechat_pay'), '2026-07-03 10:30:04'),
(8111, 8011, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'user_register_days', 100, 'logistics_complaint_count_30d', 1, 'order_amount', 79, 'order_item_count', 1, 'payment_method', 'wechat_pay'), '2026-07-03 11:45:02'),
(8112, 8012, JSON_OBJECT('is_user_blacklisted', false, 'is_order_blacklisted', false, 'user_register_days', 15, 'user_order_count_1h', 6, 'order_amount', 2100, 'order_item_count', 8, 'payment_method', 'unknown'), '2026-07-03 13:05:04');

-- ============================================================
-- 规则命中数据
-- ============================================================
INSERT INTO `rule_hits`
(`assessment_id`, `rule_id`, `hit_score`, `hit_message`, `created_at`)
VALUES
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REGISTER_NEW_HIGH_AMOUNT'), 70.00, '注册7天内的新用户发起高额订单', '2026-07-01 10:00:03'),
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ORDER_AMOUNT_HIGH'), 55.00, '订单金额超过高额阈值', '2026-07-01 10:00:03'),
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ORDER_ITEMS_HIGH'), 35.00, '单笔订单商品数量异常偏高', '2026-07-01 10:00:03'),
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'COUPON_ABUSE'), 50.00, '订单使用高折扣优惠券，存在薅羊毛风险', '2026-07-01 10:00:03'),
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'FIRST_ORDER_HIGH_AMOUNT'), 45.00, '用户首单金额异常偏高', '2026-07-01 10:00:03'),
(8001, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'PAYMENT_METHOD_RISK'), 25.00, '支付方式属于高风险或未知类型', '2026-07-01 10:00:03'),
(8003, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'AFTER_SALE_7D_HIGH'), 35.00, '用户近7天售后申请次数过多', '2026-07-01 11:20:04'),
(8004, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'LOGISTICS_COMPLAINT_REPEAT'), 30.00, '用户近30天物流投诉次数过多', '2026-07-01 12:10:03'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_BLACKLIST'), 100.00, '用户编号命中有效黑名单', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ORDER_BLACKLIST'), 95.00, '订单编号命中有效黑名单', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'PHONE_MULTI_USER'), 60.00, '同一手机号关联多个用户，存在账号团伙风险', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'DEVICE_MULTI_USER'), 65.00, '同一设备关联多个用户，存在批量注册或刷单风险', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'IP_HIGH_RISK'), 55.00, '请求IP归属高风险地区', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REGISTER_NEW_HIGH_AMOUNT'), 70.00, '注册7天内的新用户发起高额订单', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REFUND_RATE_HIGH'), 75.00, '用户近90天退款率超过30%', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_COMPLAINT_HIGH'), 40.00, '用户近90天投诉次数过多', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_HIGH_RISK_HISTORY'), 85.00, '用户历史多次被判定为高风险', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REJECT_HISTORY'), 80.00, '用户历史存在多次拒绝处置', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ORDER_AMOUNT_HIGH'), 55.00, '订单金额超过高额阈值', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'COUPON_ABUSE'), 50.00, '订单使用高折扣优惠券，存在薅羊毛风险', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ADDRESS_HIGH_RISK_AREA'), 60.00, '收货地址属于高风险地区', '2026-07-02 09:35:05'),
(8005, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'PAYMENT_METHOD_RISK'), 25.00, '支付方式属于高风险或未知类型', '2026-07-02 09:35:05'),
(8006, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REGISTER_NEW_HIGH_AMOUNT'), 70.00, '注册7天内的新用户发起高额订单', '2026-07-02 10:05:04'),
(8006, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'FIRST_ORDER_HIGH_AMOUNT'), 45.00, '用户首单金额异常偏高', '2026-07-02 10:05:04'),
(8008, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ADDRESS_USER_COUNT_HIGH'), 55.00, '同一收货地址关联多个用户', '2026-07-02 16:45:03'),
(8008, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ADDRESS_ORDER_1D_HIGH'), 50.00, '同一地址1天内订单数量过多', '2026-07-02 16:45:03'),
(8008, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ADDRESS_IP_MISMATCH'), 45.00, '收货地址与请求IP所在地不一致', '2026-07-02 16:45:03'),
(8008, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ADDRESS_HIGH_RISK_AREA'), 60.00, '收货地址属于高风险地区', '2026-07-02 16:45:03'),
(8009, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'ORDER_AMOUNT_HIGH'), 55.00, '订单金额超过高额阈值', '2026-07-03 09:10:03'),
(8010, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_REFUND_RATE_HIGH'), 75.00, '用户近90天退款率超过30%', '2026-07-03 10:30:04'),
(8010, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'AFTER_SALE_7D_HIGH'), 35.00, '用户近7天售后申请次数过多', '2026-07-03 10:30:04'),
(8012, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'USER_ORDER_1H_HIGH'), 65.00, '同一用户1小时内下单次数过多', '2026-07-03 13:05:04'),
(8012, (SELECT `id` FROM `risk_rules` WHERE `rule_code` = 'PAYMENT_METHOD_RISK'), 25.00, '支付方式属于高风险或未知类型', '2026-07-03 13:05:04');

-- ============================================================
-- 风险案件数据
-- ============================================================
INSERT INTO `risk_cases`
(`id`, `assessment_id`, `user_id`, `order_id`, `case_status`, `reviewer_id`, `review_result`, `review_remark`, `created_at`, `updated_at`)
VALUES
(9001, 8001, 'U10001', 'O10001', 'approved', 'A10001', 'approved', '确认订单金额和优惠券使用异常，建议人工放行但持续关注', '2026-07-01 10:00:06', '2026-07-01 10:25:00'),
(9002, 8005, 'U90001', 'O90001', 'rejected', 'A10002', 'rejected', '用户、订单、设备、IP 多维命中黑名单，拒绝交易', '2026-07-02 09:35:08', '2026-07-02 09:50:00'),
(9003, 8006, 'U10005', 'O10005', 'approved', 'A10001', 'approved', '新用户高额首单，电话核验通过后放行', '2026-07-02 10:05:08', '2026-07-02 11:20:00'),
(9004, 8008, 'U10007', 'O10007', 'pending', NULL, NULL, NULL, '2026-07-02 16:45:06', '2026-07-03 10:00:07'),
(9005, 8010, 'U10001', 'O10009', 'pending', NULL, NULL, NULL, '2026-07-03 10:30:07', '2026-07-03 10:30:07'),
(9006, 8012, 'U10010', 'O10011', 'pending', NULL, NULL, NULL, '2026-07-03 13:05:07', '2026-07-03 13:05:07');

-- ============================================================
-- 审核日志数据
-- ============================================================
INSERT INTO `review_logs`
(`case_id`, `operator_id`, `action_type`, `from_status`, `to_status`, `action_remark`, `created_at`)
VALUES
(9001, 'system', 'create', NULL, 'pending', '风险等级 medium，系统自动创建案件', '2026-07-01 10:00:06'),
(9001, 'A10001', 'approve', 'pending', 'approved', '确认订单金额和优惠券使用异常，建议人工放行但持续关注', '2026-07-01 10:25:00'),
(9002, 'system', 'create', NULL, 'pending', '命中黑名单规则，系统自动创建案件', '2026-07-02 09:35:08'),
(9002, 'A10002', 'reject', 'pending', 'rejected', '用户、订单、设备、IP 多维命中黑名单，拒绝交易', '2026-07-02 09:50:00'),
(9003, 'system', 'create', NULL, 'pending', '处理中风险 manual_review，系统自动创建案件', '2026-07-02 10:05:08'),
(9003, 'A10001', 'approve', 'pending', 'approved', '电话核验通过，允许继续交易', '2026-07-02 11:00:00'),
(9003, 'A10001', 'resolve', 'approved', 'resolved', '案件归档完成', '2026-07-02 11:20:00'),
(9004, 'system', 'create', NULL, 'pending', '地址维度规则累计达到中风险，系统自动创建案件', '2026-07-02 16:45:06'),
(9005, 'system', 'create', NULL, 'pending', '退款率高风险等级 high，系统自动创建案件', '2026-07-03 10:30:07'),
(9006, 'system', 'create', NULL, 'pending', '短时间下单频繁触发中风险，系统自动创建案件', '2026-07-03 13:05:07');

-- 根据演示命中数据刷新规则累计命中次数
UPDATE `risk_rules` r
LEFT JOIN (
    SELECT `rule_id`, COUNT(*) AS hit_total
    FROM `rule_hits`
    GROUP BY `rule_id`
) h ON h.`rule_id` = r.`id`
SET r.`hit_count` = COALESCE(h.`hit_total`, 0);

COMMIT;


