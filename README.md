# 💆 Zentime Masszázs Időpontfoglaló Rendszer

Ez egy Flask-alapú webalkalmazás, amely lehetőséget biztosít a felhasználóknak masszázs időpontok online foglalására, valamint az adminisztrátoroknak a szolgáltatások, foglalások és felhasználók kezelésére.

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
    git clone https://github.com/felhasznalo/zentime-masszazs.git
    cd zentime-masszazs
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
    DATABASE_URL=sqlite:///db.sqlite3
    ```

6. **Adatbázis inicializálása**

   ```bash
    python init_db.py
    ```

7. **Alkalmazás futtatása**

    ```bash
    flask run
    ```

---

## 🧪 Tesztelés

### Tesztek futtatása

```bash
python -m unittest discover
```

### Tesztlefedettség (coverage)

```bash
coverage run -m unittest discover
coverage report
```

---

## 📦 Csomagolás

A projekt pip installálható a `setup.py` segítségével:

```bash
pip install .
```

---

## 🧼 Statikus elemzés

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

Ez a projekt oktatási célra készült.
