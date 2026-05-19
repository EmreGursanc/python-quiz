# Python Quiz Web Sitesi

Flask + SQLAlchemy ile hazırlanmış, gençlere yönelik Python bilgi sınavı uygulaması.

## Özellikler
- 10 soruluk Python sınavı (Discord.py, Flask, AI, CV, NLP konuları)
- Kullanıcı skoru + kişisel en yüksek skor + global en yüksek skor
- Görsel nesne algılama (ImageAI TinyYOLO)
- SQLite veritabanı
- PythonAnywhere üzerinde yayında

## Kurulum

### 1. Gerekli kütüphaneleri yükle
```
pip install -r requirements.txt
```

### 2. Model dosyasını indir
`yolo-tiny.h5` dosyasını şuradan indir ve `models/` klasörüne koy:
https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/tiny-yolov3.pt/

### 3. Klasör yapısı
```
python-pro/
├── app.py
├── models/
│   └── yolo-tiny.h5
├── static/
│   ├── style.css
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── quiz.html
│   ├── result.html
│   └── detect.html
├── requirements.txt
└── README.md
```

### 4. Uygulamayı çalıştır
```
python app.py
```

## PythonAnywhere Yayınlama
1. PythonAnywhere'de yeni bir web app oluştur (Flask seç)
2. Dosyaları yükle
3. `requirements.txt` içindeki paketleri bash console üzerinden kur
4. WSGI dosyasında uygulama yolunu ayarla
5. Reload et
