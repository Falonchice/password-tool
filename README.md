# Local Password Manager

本项目为一个基于 Python 的本地加密密码管理器，数据仅在本地保存，界面采用 Tkinter，支持主密码加密、剪贴板、导入导出、密码生成、自动锁定等常用功能。

## 功能特性

- 本地加密存储所有密码，安全可靠
- 主密码保护，防止未授权访问
- 支持密码的增删查改
- 支持搜索、导入和导出 JSON 文件
- 支持生成随机密码并自动复制到剪贴板
- 密码一键复制
- 自动锁定（超时需重新输入主密码）
- 中文友好界面

## 安装依赖

建议使用 Python 3.7 及以上版本。

```bash
pip install -r requirements.txt
```

## 启动方法

```bash
python gui.py
```

首次运行会要求设置主密码，之后每次启动都需输入主密码。

## 文件说明

- `gui.py`：主程序，Tkinter 界面
- `password_db.py`：本地加密数据库实现
- `requirements.txt`：依赖库清单

## 依赖库

- pycryptodome
- pyperclip

## 数据安全说明

所有数据均加密存储于本地文件（`passwords.db`），不会上传云端，请妥善保管主密码，遗忘主密码数据将无法恢复。

## 截图


## License

MIT
