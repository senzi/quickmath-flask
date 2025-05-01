# QuickMath 速算练习平台

QuickMath 是一个基于 Flask 的在线速算训练平台，支持多种题型模块、自动批卷、历史记录、移动端适配，适合学生和速算爱好者日常练习。

## 功能特性

- 支持多种题型（两位×一位、加减混合、三位加减、多位÷两位、多位÷三位）
- 题型与题量可自定义，支持题型顺序/乱序出题
- 答题自动缓存，防丢失，页面刷新可恢复
- 自动批卷，显示得分与正确率
- 历史记录保存每次练习详情，可随时回顾
- 移动端友好，界面简洁美观
- 支持局域网访问

## 安装与运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 初始化数据库

```bash
flask initdb
```

3. 启动服务（支持局域网访问）

```bash
python app.py
```
或
```bash
flask run --host=0.0.0.0
```

4. 浏览器访问

- 本机访问：http://127.0.0.1:5000
- 局域网访问：http://<本机IP>:5000

## 清空历史记录

```bash
sqlite3 quickmath.db "DELETE FROM history; DELETE FROM question;"
```
如未安装 sqlite3，可用 Flask shell：
```python
flask shell
>>> from app import db, History, Question
>>> db.session.query(History).delete()
>>> db.session.query(Question).delete()
>>> db.session.commit()
```

## 目录结构

```
quickmath-flask/
├── app.py                # Flask 主程序
├── requirements.txt
├── README.md
├── templates/            # 页面模板
├── static/               # 静态资源
├── quickmath.db          # SQLite 数据库
└── doc/PRD.md            # 产品需求文档
```

## 技术栈

- Python 3.x
- Flask / Flask-SQLAlchemy
- Jinja2
- Bootstrap 5
- SQLite

## 其他说明

- 支持移动端浏览
- 答题过程自动缓存，防止刷新丢失
- 题型与题量、顺序/乱序均可自定义
- 历史记录支持详情回顾

如有问题欢迎反馈！
