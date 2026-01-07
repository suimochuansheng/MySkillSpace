-- ==========================================
-- 添加"封禁IP管理"菜单到数据库
-- 执行方式：在服务器上执行此SQL脚本
-- ==========================================

-- 1. 查找"系统管理"菜单的ID（作为父菜单）
SET @system_menu_id = (SELECT id FROM sys_menu WHERE name = '系统管理' LIMIT 1);

-- 2. 插入"封禁IP管理"菜单（菜单类型）
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
    '封禁IP管理',                          -- 菜单名称
    '/sys/banned-ip',                       -- 前端路由路径
    'sys/banned-ip/index',                  -- Vue组件路径
    'C',                                    -- 菜单类型：C=菜单
    'monitor:banned:list',                  -- 权限标识
    'Lock',                                 -- 图标
    6,                                      -- 排序（在登录日志之后）
    @system_menu_id,                        -- 父级菜单ID
    NOW(),                                  -- 创建时间
    NOW()                                   -- 更新时间
);

-- 获取刚插入的菜单ID
SET @banned_ip_menu_id = LAST_INSERT_ID();

-- 3. 插入"解封IP"按钮权限（按钮类型）
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
    '解封IP',                               -- 按钮名称
    '',                                     -- 按钮无路径
    '',                                     -- 按钮无组件
    'F',                                    -- 菜单类型：F=按钮
    'monitor:banned:unban',                 -- 权限标识
    '',                                     -- 按钮无图标
    1,                                      -- 排序
    @banned_ip_menu_id,                     -- 父级菜单ID（封禁IP管理）
    NOW(),                                  -- 创建时间
    NOW()                                   -- 更新时间
);

-- 4. 将新菜单分配给管理员角色
-- 查找管理员角色ID
SET @admin_role_id = (SELECT id FROM sys_role WHERE code = 'admin' LIMIT 1);

-- 将"封禁IP管理"菜单分配给管理员
INSERT INTO sys_role_menu (role_id, menu_id)
VALUES (@admin_role_id, @banned_ip_menu_id);

-- 将"解封IP"按钮权限分配给管理员
INSERT INTO sys_role_menu (role_id, menu_id)
VALUES (@admin_role_id, LAST_INSERT_ID());

-- 5. 验证插入结果
SELECT
    m.id,
    m.name,
    m.path,
    m.perms,
    m.menu_type,
    m.order_num,
    p.name AS parent_name
FROM sys_menu m
LEFT JOIN sys_menu p ON m.parent_id = p.id
WHERE m.name IN ('封禁IP管理', '解封IP')
ORDER BY m.id;

-- 显示提示
SELECT '✅ 封禁IP管理菜单已成功添加！请重新登录查看。' AS message;
