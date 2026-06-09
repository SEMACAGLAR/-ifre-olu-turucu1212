from flask import Flask, render_template, request, jsonify
import random
import string

app = Flask(__name__)

# --- Şifre güçlülüğünü hesaplar ---
def guc_hesapla(sifre):
    puan = 0
    if any(c.isupper() for c in sifre):
        puan += 1
    if any(c.islower() for c in sifre):
        puan += 1
    if any(c.isdigit() for c in sifre):
        puan += 1
    if any(c in "!@#$%^&*" for c in sifre):
        puan += 1
    if len(sifre) >= 16:
        puan += 1

    if puan <= 2:
        return "Zayıf"
    elif puan == 3:
        return "Orta"
    elif puan == 4:
        return "Güçlü"
    else:
        return "Çok Güçlü"

# --- Karakter havuzunu oluşturur ---
def karakter_havuzu_olustur(buyuk, kucuk, rakam, sembol):
    havuz = ""
    if buyuk:
        havuz += string.ascii_uppercase
    if kucuk:
        havuz += string.ascii_lowercase
    if rakam:
        havuz += string.digits
    if sembol:
        havuz += "!@#$%^&*"
    return havuz

# --- Şifreyi rastgele oluşturur ---
def sifre_olustur(uzunluk, buyuk, kucuk, rakam, sembol):
    havuz = karakter_havuzu_olustur(buyuk, kucuk, rakam, sembol)

    if not havuz:
        return None, "En az bir karakter türü seçmelisiniz."

    zorunlu = []
    if buyuk:
        zorunlu.append(random.choice(string.ascii_uppercase))
    if kucuk:
        zorunlu.append(random.choice(string.ascii_lowercase))
    if rakam:
        zorunlu.append(random.choice(string.digits))
    if sembol:
        zorunlu.append(random.choice("!@#$%^&*"))

    kalan_uzunluk = uzunluk - len(zorunlu)
    rastgele = [random.choice(havuz) for _ in range(kalan_uzunluk)]

    tum_karakterler = zorunlu + rastgele
    random.shuffle(tum_karakterler)

    sifre = "".join(tum_karakterler)
    return sifre, None

# --- Birden fazla şifre üretir ---
def coklu_sifre_olustur(adet, uzunluk, buyuk, kucuk, rakam, sembol):
    sifreler = []
    for _ in range(adet):
        sifre, hata = sifre_olustur(uzunluk, buyuk, kucuk, rakam, sembol)
        if hata:
            return None, hata
        sifreler.append(sifre)
    return sifreler, None

# --- Ana sayfa ---
@app.route("/")
def index():
    return render_template("index.html")

# --- Şifre oluşturma endpoint'i ---
@app.route("/olustur", methods=["POST"])
def olustur():
    veri = request.json

    uzunluk = int(veri.get("uzunluk", 12))
    buyuk   = veri.get("buyuk", True)
    kucuk   = veri.get("kucuk", True)
    rakam   = veri.get("rakam", True)
    sembol  = veri.get("sembol", False)
    adet    = int(veri.get("adet", 1))

    if uzunluk < 4:
        return jsonify({"hata": "Şifre en az 4 karakter olmalıdır."}), 400
    if uzunluk > 64:
        return jsonify({"hata": "Şifre en fazla 64 karakter olabilir."}), 400
    if adet < 1 or adet > 10:
        return jsonify({"hata": "Adet 1 ile 10 arasında olmalıdır."}), 400

    sifreler, hata = coklu_sifre_olustur(adet, uzunluk, buyuk, kucuk, rakam, sembol)

    if hata:
        return jsonify({"hata": hata}), 400

    sonuclar = [{"sifre": s, "guc": guc_hesapla(s)} for s in sifreler]

    return jsonify({"sonuclar": sonuclar})

if __name__ == "__main__":
    app.run(debug=True)
