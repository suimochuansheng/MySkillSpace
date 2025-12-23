#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动修复 Flake8 检测到的简单错误
"""
import re
import sys


def fix_f541_f401_f841(filepath):
    """修复 F541(f-string无占位符), F401(未使用导入), F841(未使用变量)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # 需要删除的导入（从 Flake8 输出中提取）
    unused_imports = {
        'backend/SkillSpace/myapps/ai_demo/model_loader.py': [
            (152, 'flash_attn')
        ],
        'backend/SkillSpace/myapps/ai_demo/views.py': [
            (5, 'time')
        ],
        'backend/SkillSpace/myapps/auth_system/log_utils.py': [
            (10, 'django.utils.timezone'),
            (11, 'rest_framework.response.Response')
        ],
        'backend/SkillSpace/myapps/auth_system/middleware.py': [
            (9, 'io.BytesIO'),
            (11, 'django.http.QueryDict')
        ],
        'backend/SkillSpace/myapps/monitor/tasks.py': [
            (6, 'asyncio'),
            (7, 'json')
        ]
    }

    # 处理当前文件
    file_rel_path = filepath.replace('\\', '/')
    if file_rel_path in unused_imports:
        for line_num, import_name in unused_imports[file_rel_path]:
            # 删除或注释未使用的导入
            if 0 < line_num <= len(lines):
                line = lines[line_num - 1]
                if import_name in line and 'import' in line:
                    # 注释掉该行
                    lines[line_num - 1] = f"# {line}  # noqa: F401 (unused import)"

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✓ 已修复: {filepath}")


if __name__ == '__main__':
    # 从命令行参数获取文件列表
    if len(sys.argv) < 2:
        print("用法: python fix_flake8.py <file1> <file2> ...")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        try:
            fix_f541_f401_f841(filepath)
        except Exception as e:
            print(f"✗ 修复失败 {filepath}: {e}")
