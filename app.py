from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'gizlikey2024abc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16mb

db = SQLAlchemy(app)


# --- modeller ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    results = db.relationship('QuizResult', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DetectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(200))
    result_json = db.Column(db.Text)  # json string olarak tutuyoruz
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- sorular ---

QUESTIONS = [
    {
        "id": 1,
        "topic": "Discord.py - Sohbet Botu",
        "question": "Discord.py'de bir bot komutu tanımlamak için hangi dekoratör kullanılır?",
        "choices": ["@bot.command()", "@bot.event()", "@client.command()", "@discord.command()"],
        "answer": 0
    },
    {
        "id": 2,
        "topic": "Discord.py - Sohbet Botu",
        "question": "Bir Discord botunu TOKEN ile başlatmak için hangi metod kullanılır?",
        "choices": ["bot.start(TOKEN)", "bot.run(TOKEN)", "bot.launch(TOKEN)", "bot.connect(TOKEN)"],
        "answer": 1
    },
    {
        "id": 3,
        "topic": "Flask - Web Geliştirme",
        "question": "Flask'ta URL rotası tanımlamak için kullanılan dekoratör hangisidir?",
        "choices": ["@flask.route()", "@app.url()", "@app.route()", "@app.path()"],
        "answer": 2
    },
    {
        "id": 4,
        "topic": "Flask - Web Geliştirme",
        "question": "Flask'ta bir HTML şablon dosyasını render etmek için hangi fonksiyon kullanılır?",
        "choices": ["render('template.html')", "render_template('template.html')", "flask.render('template.html')", "app.render('template.html')"],
        "answer": 1
    },
    {
        "id": 5,
        "topic": "Python ile Yapay Zeka",
        "question": "TensorFlow/Keras'ta bir sinir ağı modelini eğitmek için hangi metod kullanılır?",
        "choices": ["model.train()", "model.run()", "model.fit()", "model.start()"],
        "answer": 2
    },
    {
        "id": 6,
        "topic": "Python ile Yapay Zeka",
        "question": "Keras Sequential modeline yeni katman eklemek için hangi metod kullanılır?",
        "choices": ["model.insert()", "model.add()", "model.append()", "model.push()"],
        "answer": 1
    },
    {
        "id": 7,
        "topic": "Bilgisayar Görüşü - Computer Vision",
        "question": "ImageAI'de nesne tespiti yapan sınıf hangisidir?",
        "choices": ["ImageDetector", "YOLODetection", "ObjectDetection", "ImageAI.Detect"],
        "answer": 2
    },
    {
        "id": 8,
        "topic": "Bilgisayar Görüşü - Computer Vision",
        "question": "OpenCV'de görüntüyü gri tonlamaya çeviren fonksiyon hangisidir?",
        "choices": [
            "cv2.toGray(img)",
            "cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)",
            "cv2.gray(img)",
            "cv2.convert(img, 'gray')"
        ],
        "answer": 1
    },
    {
        "id": 9,
        "topic": "Doğal Dil İşleme - NLP",
        "question": "NLTK ile bir metni kelimelere bölmek için hangi fonksiyon kullanılır?",
        "choices": ["nltk.split(text)", "nltk.tokenize(text)", "nltk.word_tokenize(text)", "nltk.parse(text)"],
        "answer": 2
    },
    {
        "id": 10,
        "topic": "Doğal Dil İşleme - NLP",
        "question": "BeautifulSoup ile sayfadaki tüm <p> etiketlerini bulmak için hangi metod kullanılır?",
        "choices": ["soup.find('p')", "soup.get_all('p')", "soup.find_all('p')", "soup.select('p', all=True)"],
        "answer": 2
    }
]


# --- yardımcı fonksiyonlar ---

def get_global_best():
    # tüm kullanıcılar arasındaki en yüksek skor
    best = db.session.query(db.func.max(QuizResult.score)).scalar()
    return best if best is not None else 0


def get_user_best(user_id):
    # sadece bu kullanıcının en yüksek skoru
    best = db.session.query(db.func.max(QuizResult.score)).filter_by(user_id=user_id).scalar()
    return best if best is not None else 0


# --- rotalar ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Kullanıcı adı boş olamaz!')
            return redirect(url_for('index'))

        # kullanıcı varsa getir yoksa oluştur
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('quiz'))

    global_best = get_global_best()
    user_best = 0
    if 'user_id' in session:
        user_best = get_user_best(session['user_id'])

    return render_template('index.html', global_best=global_best, user_best=user_best)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    global_best = get_global_best()
    user_best = get_user_best(session['user_id'])

    if request.method == 'POST':
        score = 0
        total = len(QUESTIONS)

        for q in QUESTIONS:
            answer = request.form.get(f"q{q['id']}")
            # cevap geldiyse ve doğruysa puan ver
            if answer is not None and int(answer) == q['answer']:
                score += 1

        # sonucu veritabanına kaydet
        result = QuizResult(user_id=session['user_id'], score=score, total=total)
        db.session.add(result)
        db.session.commit()

        session['last_score'] = score
        session['last_total'] = total

        return redirect(url_for('result'))

    return render_template('quiz.html', questions=QUESTIONS, global_best=global_best, user_best=user_best)


@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    global_best = get_global_best()
    user_best = get_user_best(session['user_id'])
    last_score = session.get('last_score', 0)
    last_total = session.get('last_total', len(QUESTIONS))

    return render_template('result.html',
                           score=last_score,
                           total=last_total,
                           global_best=global_best,
                           user_best=user_best,
                           username=session.get('username'))


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    global_best = get_global_best()
    user_best = get_user_best(session['user_id'])
    predictions = None
    image_path = None
    error_msg = None

    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Dosya seçilmedi!')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('Dosya seçilmedi!')
            return redirect(request.url)

        if file:
            filename = file.filename
            upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)

            try:
                import requests as req

                # huggingface ücretsiz inference api ile sınıflandırma
                HF_URL = "https://api-inference.huggingface.co/models/google/mobilenet_v2_1.0_224"

                with open(save_path, "rb") as img_file:
                    img_data = img_file.read()

                response = req.post(HF_URL, data=img_data, timeout=30)

                # model henüz yüklenmediyse biraz bekle ve tekrar dene
                if response.status_code == 503:
                    import time
                    time.sleep(10)
                    response = req.post(HF_URL, data=img_data, timeout=30)

                if response.status_code != 200:
                    raise Exception(f"API Hatası (Kod: {response.status_code}): {response.text}")

                raw_results = response.json()

                # print(raw_results)  # test sırasında açtım

                predictions = []
                if isinstance(raw_results, list):
                    for item in raw_results[:5]:
                        predictions.append({
                            'name': item.get('label', 'bilinmiyor').replace('_', ' '),
                            'confidence': round(float(item.get('score', 0)) * 100, 2)
                        })

                # veritabanına kaydet
                log = DetectionLog(
                    image_name=filename,
                    result_json=json.dumps(predictions, ensure_ascii=False)
                )
                db.session.add(log)
                db.session.commit()

                image_path = 'uploads/' + filename

            except Exception as e:
                error_msg = f"Hata oluştu: {str(e)}"
                # print(e)

    return render_template('detect.html',
                           predictions=predictions,
                           image_path=image_path,
                           error_msg=error_msg,
                           global_best=global_best,
                           user_best=user_best)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
