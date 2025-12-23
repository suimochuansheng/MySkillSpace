import os
import shutil

# 1. 设置根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 设置需要【避开】的目录名 (非常重要！)
IGNORE_DIRS = ["sk_venv", "venv", ".git", ".idea", "__pycache__", "site-packages"]

print(f"正在清理项目：{BASE_DIR}")
print(f"安全模式：将跳过以下目录 {IGNORE_DIRS}")

for root, dirs, files in os.walk(BASE_DIR):
    # 修改 dirs 列表，让 os.walk 跳过忽略的目录
    # 必须倒序遍历删除，否则会跳过某些目录
    for d in dirs[:]:
        if d in IGNORE_DIRS or "venv" in d:
            dirs.remove(d)
            print(f"已跳过系统目录: {d}")

    # 1. 清理 __pycache__
    if "__pycache__" in dirs:
        pycache_path = os.path.join(root, "__pycache__")
        try:
            shutil.rmtree(pycache_path)
            dirs.remove("__pycache__")
            print(f"删除缓存目录: {pycache_path}")
        except Exception as e:
            pass

    # 2. 清理 migrations
    if "migrations" in os.path.basename(root):
        # 双重保险：再次检查当前路径是否包含 venv 关键字
        if "sk_venv" in root or "site-packages" in root:
            continue

        for file in files:
            if file != "__init__.py" and (
                file.endswith(".py") or file.endswith(".pyc")
            ):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已清理旧迁移文件: {file_path}")
                except Exception as e:
                    print(f"删除失败: {file_path} {e}")

print("-----------------------------------")
print("清理完成。现在可以运行 makemigrations 了。")
