import random
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'quickmath-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quickmath.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ 数据库模型 ------------------

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(32))
    config = db.Column(db.String(256))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    questions = db.relationship('Question', backref='history', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'), nullable=False)
    type = db.Column(db.String(32))
    stem = db.Column(db.String(128))
    answer = db.Column(db.String(64))
    user_answer = db.Column(db.String(64))
    is_correct = db.Column(db.Boolean)

# ------------------ 题型与生成 ------------------

def generate_mul2x1():
    a = random.randint(10, 99)
    b = random.randint(2, 9)
    return {
        'type': 'mul2x1',
        'stem': f'{a} × {b} = ',
        'answer': str(a * b)
    }

def generate_addsub2():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    add = a + b
    sub = a - b
    return {
        'type': 'addsub2',
        'stem': f'{a}  {b}',
        'answer': json.dumps({'add': str(add), 'sub': str(sub)})
    }

def generate_addsub3():
    a = random.randint(100, 999)
    b = random.randint(100, 999)
    add = a + b
    sub = a - b
    return {
        'type': 'addsub3',
        'stem': f'{a}  {b}',
        'answer': json.dumps({'add': str(add), 'sub': str(sub)})
    }

def generate_div2():
    b = random.randint(12, 99)
    # 计算k的范围，使a为5位数
    k_min = (10000 + b - 1) // b
    k_max = 99999 // b
    k = random.randint(k_min, k_max)
    a = b * k
    q = a // b
    return {
        'type': 'div2',
        'stem': f'{a} ÷ {b} = ',
        'answer': str(str(q)[0])  # 只答商首位
    }

def generate_div3():
    b = random.randint(100, 999)
    k_min = (10000 + b - 1) // b
    k_max = 99999 // b
    k = random.randint(k_min, k_max)
    a = b * k
    q = a // b
    return {
        'type': 'div3',
        'stem': f'{a} ÷ {b} = ',
        'answer': str(q)[:2]  # 只答商前两位
    }

GENERATOR_MAP = {
    'mul2x1': generate_mul2x1,
    'addsub2': generate_addsub2,
    'addsub3': generate_addsub3,
    'div2': generate_div2,
    'div3': generate_div3,
}

# ------------------ 路由 ------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        types = request.form.getlist('types')
        config = {}
        questions = []
        for t in types:
            count = int(request.form.get(f'count_{t}', 10))
            config[t] = count
            for _ in range(count):
                q = GENERATOR_MAP[t]()
                q['id'] = f"{t}_{random.randint(100000,999999)}"
                questions.append(q)
        shuffle = request.form.get('shuffle')
        if shuffle:
            random.shuffle(questions)
        # 不勾选则保持题型顺序
        session['questions'] = questions
        session['config'] = config
        session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return redirect(url_for('quiz'))
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = session.get('questions')
    if not questions:
        return redirect(url_for('index'))
    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    questions = session.get('questions')
    if not questions:
        return redirect(url_for('index'))
    results = []
    score = 0
    total = len(questions)
    for q in questions:
        qid = q['id']
        qtype = q['type']
        correct = False
        user_answer = ''
        if qtype in ['addsub2', 'addsub3']:
            ua1 = request.form.get(f'answer_{qid}_1', '').strip()
            ua2 = request.form.get(f'answer_{qid}_2', '').strip()
            user_answer = json.dumps({'add': ua1, 'sub': ua2})
            ans = json.loads(q['answer'])
            correct = (ua1 == ans['add'] and ua2 == ans['sub'])
        else:
            ua = request.form.get(f'answer_{qid}', '').strip()
            user_answer = ua
            if qtype == 'div2':
                correct = (ua == q['answer'])
            elif qtype == 'div3':
                correct = (ua == q['answer'])
            else:
                correct = (ua == q['answer'])
        if correct:
            score += 1
        results.append({
            'stem': q['stem'],
            'type': qtype,
            'answer': q['answer'] if qtype not in ['addsub2', 'addsub3'] else json.loads(q['answer']),
            'user_answer': user_answer if qtype not in ['addsub2', 'addsub3'] else json.loads(user_answer),
            'is_correct': correct
        })
    accuracy = round(score / total * 100, 2) if total else 0
    # 保存历史
    config = session.get('config', {})
    hist = History(
        timestamp=session.get('start_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        config=json.dumps(config, ensure_ascii=False),
        score=score,
        total=total,
        accuracy=accuracy
    )
    db.session.add(hist)
    db.session.commit()
    for idx, r in enumerate(results):
        q = Question(
            history_id=hist.id,
            type=questions[idx]['type'],
            stem=questions[idx]['stem'],
            answer=json.dumps(r['answer'], ensure_ascii=False) if isinstance(r['answer'], dict) else r['answer'],
            user_answer=json.dumps(r['user_answer'], ensure_ascii=False) if isinstance(r['user_answer'], dict) else r['user_answer'],
            is_correct=r['is_correct']
        )
        db.session.add(q)
    db.session.commit()
    return render_template('result.html', results=results, score=score, total=total, accuracy=accuracy)

@app.route('/history')
def history():
    hlist = History.query.order_by(History.id.desc()).all()
    def config_to_tags(config_json):
        try:
            d = json.loads(config_json)
            type_map = {
                "mul2x1": "两位×一位",
                "addsub2": "两位加减",
                "addsub3": "三位加减",
                "div2": "÷两位",
                "div3": "÷三位"
            }
            return [f"{type_map.get(k, k)}×{v}" for k, v in d.items()]
        except Exception:
            return [config_json]
    history_data = []
    for h in hlist:
        history_data.append({
            'id': h.id,
            'timestamp': h.timestamp,
            'config_tags': config_to_tags(h.config),
            'score': h.score,
            'total': h.total,
            'accuracy': h.accuracy
        })
    return render_template('history.html', history=history_data, record=None)

@app.route('/history/<int:id>')
def history_detail(id):
    h = History.query.get_or_404(id)
    qs = Question.query.filter_by(history_id=id).all()
    questions = []
    for q in qs:
        ans = q.answer
        ua = q.user_answer
        if q.type in ['addsub2', 'addsub3']:
            ans = json.loads(ans)
            ua = json.loads(ua) if ua else {'add': '', 'sub': ''}
        questions.append({
            'stem': q.stem,
            'type': q.type,
            'answer': ans,
            'user_answer': ua,
            'is_correct': q.is_correct
        })
    record = {
        'timestamp': h.timestamp,
        'config': h.config,
        'score': h.score,
        'total': h.total,
        'accuracy': h.accuracy,
        'questions': questions
    }
    return render_template('history.html', record=record, history=None)

# ------------------ 初始化数据库 ------------------
@app.cli.command('initdb')
def initdb():
    db.create_all()
    print('数据库已初始化。')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
