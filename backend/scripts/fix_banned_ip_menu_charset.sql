-- ==========================================
-- 修复"封禁IP管理"菜单的字符编码问题
-- 如果菜单显示乱码，执行此脚本
-- 使用方法：
--   docker exec -i skillspace_db mysql -uroot -p${ROOT_PASSWORD} ${DB_NAME} < fix_banned_ip_menu_charset.sql
-- ==========================================

-- 设置客户端字符集为UTF-8
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 删除可能存在的旧菜单（包含乱码的）
DELETE FROM sys_menu WHERE path = '/sys/banned-ip' OR perms LIKE 'monitor:banned:%';

-- 重新插入正确的菜单（UTF-8编码）
-- 1. 查找"系统管理"菜单的ID
SET @system_menu_id = (SELECT id FROM sys_menu WHERE name = '系统管理' LIMIT 1);

-- 2. 插入"封禁IP管理"菜单
INSERT INTO sys_menu (
    name,
    path,
    component,
    menu_type,
    perms,
    icon,
    order_num,
    parent_id,
    create_time,
    update_time
) VALUES (
    '封禁IP管理',
    '/sys/banned-ip',
    'sys/banned-ip/index',
    'C',
    'monitor:banned:list',
    'Lock',
    6,
    @system_menu_id,
    NOW(),
    NOW()
);

SET @banned_ip_menu_id = LAST_INSERT_ID();

-- 3. 插入"解封IP"按钮
INSERT INTO sys_menu (
    name,
    path,
    component,
    menu_type,
    perms,
    icon,
    order_num,
    parent_id,
    create_time,
    update_time
) VALUES (
    '解封IP',
    '',
    '',
    'F',
    'monitor:banned:unban',
    '',
    1,
    @banned_ip_menu_id,
    NOW(),
    NOW()
);

-- 4. 分配给管理员角色
SET @admin_role_id = (SELECT id FROM sys_role WHERE code = 'admin' LIMIT 1);

-- 先删除可能存在的旧关联
DELETE FROM sys_role_menu WHERE menu_id IN (
    SELECT id FROM sys_menu WHERE path = '/sys/banned-ip' OR perms LIKE 'monitor:banned:%'
);

-- 重新分配
INSERT INTO sys_role_menu (role_id, menu_id)
VALUES (@admin_role_id, @banned_ip_menu_id);

INSERT INTO sys_role_menu (role_id, menu_id)
VALUES (@admin_role_id, LAST_INSERT_ID());

-- 5. 验证结果
SELECT
    m.id,
    m.name,
    m.path,
    m.perms,
    m.menu_type,
    HEX(m.name) AS name_hex,  -- 显示十六进制，用于检查编码
    LENGTH(m.name) AS name_length,
    CHAR_LENGTH(m.name) AS name_chars
FROM sys_menu m
WHERE m.path = '/sys/banned-ip' OR m.perms LIKE 'monitor:banned:%'
ORDER BY m.id;

SELECT '✅ 字符编码已修复！请重新登录前端查看。' AS message;
