# 💆 Zentime Masszázs Időpontfoglaló Rendszer

Webalapú időpontfoglaló alkalmazás Flask keretrendszerrel, profilkezeléssel, admin funkciókkal és email értesítésekkel.

---

## 🧩 Funkciók

### Felhasználók számára:
- Regisztráció, bejelentkezés, kijelentkezés
- Profiladatok szerkesztése (jelszóval történő megerősítéssel)
- Foglalás jövőbeli időpontokra (félórás bontásban, 8:00–20:00 között)
- Időpontblokkolás ±30 perces eltolással
- Saját foglalások listázása, szerkesztése, törlése
- Google Calendar kompatibilis `.ics` export
- Hétvégére történő foglalás kizárása

### Admin számára:
- Admin dashboard felület
- Felhasználók listázása, törlése (admin nem törölhető)
- Szolgáltatások hozzáadása, módosítása, törlése (képfeltöltéssel)
- Foglalások megtekintése
- Statisztikák: szolgáltatások szerinti eloszlás, heti foglalási trendek (Chart.js)

---

## ⚙️ Telepítés

1. **Környezeti követelmények**
    - Python 3.9+
    - pip / virtualenv

2. **Repo klónozása**

    ```bash
    git clone https://github.com/RakDavid/massage_booking.git
    cd massage_booking
    ```

3. **Virtuális környezet létrehozása és aktiválása**

    - **Linux/macOS**:

        ```bash
        python -m venv venv
        source venv/bin/activate
        ```

    - **Windows**:

        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

4. **Követelmények telepítése**

    ```bash
    pip install -r requirements.txt
    ```

5. **Környezeti változók létrehozása**

    Hozz létre egy `.env` fájlt az alábbi tartalommal:

    ```
    SECRET_KEY=nagyon-titkos-kulcs
    DATABASE_URL=sqlite:///db.sqlite3
    
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=zentimedemo@gmail.com
    MAIL_PASSWORD=zegesfhaemiuttuv
    MAIL_DEFAULT_SENDER_EMAIL=zentimedemo@gmail.com
    MAIL_DEFAULT_SENDER_NAME=Zentime Masszázs Stúdió
    
    ```

6. **A projekt pip installálása `setup.py` segítségével**

    ```bash
    pip install .
    ```

7. **Alkalmazás futtatása**

    ```bash
    flask run
    ```

---

## 🧪 Tesztelés

A projekthez `unittest` alapú egységtesztek készültek a `coverage` segítségével, amelyek lefedik a legfontosabb funkciókat, beleértve a bejelentkezést, regisztrációt, időpontfoglalást, admin műveleteket, profilmódosítást és .ics exportálást. Az erről készült jelentést `reports/coverage.txt` fájlban csatoltam a beadáshoz

### Tesztek futtatása

```bash
python -m unittest discover -s tests -p "*_test.py"
```

### Tesztlefedettség (coverage)

```bash
coverage run -m unittest discover -s tests -p "*_test.py"
coverage report
```

---

## 🧼 Statikus elemzés

A `flake8` és `pylint` kódelemzők használatával ellenőriztem a projektet. A jelentéseket `reports/lint_report.txt` és `reports/flake8_report.txt` fájlokban csatoltam a beadáshoz.

### PEP8 ellenőrzés

```bash
flake8 app/
```

### Kódminőség-ellenőrzés

```bash
pylint app/
```
---

## 🔐 Jogosultságkezelés

- Admin jog: `is_admin=True`
- Az admin user adatait megtalálhatod az init_db.py fájlban
- Route védelem: `@login_required`, `current_user.is_admin`

---

## 📬 Email támogatás

Az alkalmazás támogatja a jövőbeni email értesítések küldését a `Flask-Mail` segítségével (alapbeállításokat `.env` fájlban kell megadni).

---

## 📃 Licenc

Ez a projekt oktatási célra készült, kereskedelmi felhasználása nem engedélyezett.
