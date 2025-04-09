"""A masszázs időpontfoglaló alkalmazás nézetei
    (route-ok és view-függvények)."""

from datetime import datetime, timedelta, date, \
    time
import os

from flask import Response, Blueprint, jsonify, \
    render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, \
    login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, \
    check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from ics import Calendar, Event

from .forms import RegisterForm, LoginForm, BookingForm, \
    ServiceForm, ProfileUpdateForm
from .models import User, Booking, MassageService
from . import db, mail


main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Főoldal, ahol a szolgáltatások listázva vannak."""
    services = MassageService.query.all()
    return render_template('index.html', services=services)


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Felhasználói regisztrációs űrlap megjelenítése és feldolgozása."""
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Ez az e-mail már regisztrálva van.', "error")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Sikeres regisztráció!', "success")
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Bejelentkezési űrlap kezelése és autentikáció."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Sikeres bejelentkezés!', "success")
            return redirect(url_for('main.index'))
        flash('Hibás bejelentkezési adatok.', "error")
    return render_template('login.html', form=form)


@main.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    """Új időpont foglalása. Elérhető időpontok számítása és ellenőrzés."""
    form = BookingForm()

    preselected_date = request.args.get('date')
    preselected_time = request.args.get('time')

    if preselected_date:
        selected_date = datetime.strptime(preselected_date, '%Y-%m-%d').date()
        form.date.data = selected_date
    else:
        selected_date = form.date.data or date.today()
        form.date.data = selected_date

    if request.method == 'GET' and 'date' in \
            request.args and request.args.get('date'):
        selected_date = datetime.strptime(
            request.args.get('date'), '%Y-%m-%d').date()
        form.date.data = selected_date
    else:
        form.date.data = form.date.data or date.today()
        selected_date = form.date.data

    services = MassageService.query.all()
    form.service.choices = [(s.name, s.name) for s in services]

    preselected_service = request.args.get('service')
    if preselected_service and preselected_service in \
            [s.name for s in services]:
        form.service.data = preselected_service

    all_times = [
        (datetime.combine(selected_date, time(8, 0)) +
            timedelta(minutes=30 * i)).time()
        for i in range(25)
    ]
    all_times_str = [t.strftime('%H:%M') for t in all_times]

    bookings = Booking.query.filter_by(date=selected_date).all()

    blocked_set = set()
    for b in bookings:
        booked_time = datetime.strptime(b.time, "%H:%M").time()
        for offset in [-30, 0, 30]:
            blocked = (
                datetime.combine(selected_date, booked_time)
                + timedelta(minutes=offset)).time()
            blocked_set.add(blocked)

    blocked_times = [t.strftime('%H:%M') for t in blocked_set]
    now = datetime.now().replace(second=0, microsecond=0)
    is_today = selected_date == now.date()

    available_times = [
        t.strftime('%H:%M') for t in all_times
        if t.strftime('%H:%M') not in blocked_times and
        (not is_today or datetime.combine(selected_date, t) > now)
    ]

    if preselected_time and preselected_time in available_times:
        form.time.data = datetime.strptime(preselected_time, '%H:%M').time()

    if form.validate_on_submit():
        selected_time = form.time.data
        selected_datetime = datetime.combine(selected_date, selected_time)
        now = datetime.now()

        if selected_datetime <= now:
            flash("Csak a jelenlegi időpont utánra foglalhatsz.", "error")
            return render_template(
                'booking.html',
                form=form,
                all_times=all_times_str,
                blocked_times=blocked_times,
                available_times=available_times
            )
        if selected_datetime.weekday() in [5, 6]:
            flash("Hétvégére nem lehet foglalni.", "error")
            return render_template(
                'booking.html',
                form=form,
                all_times=all_times_str,
                blocked_times=blocked_times,
                available_times=available_times
            )
        times_to_check = [
            (selected_datetime - timedelta(minutes=30)).time(),
            selected_time,
            (selected_datetime + timedelta(minutes=30)).time()
        ]
        conflicts = Booking.query.filter_by(date=selected_date).filter(
            Booking.time.in_([t.strftime('%H:%M') for t in times_to_check])
        ).first()

        if conflicts:
            flash(
                "Ez az időpont vagy annak közvetlen előtte/utána "
                "lévő félórája már foglalt.", "error")
            return render_template(
                'booking.html',
                form=form,
                all_times=all_times_str,
                blocked_times=blocked_times,
                available_times=available_times
            )
        new_booking = Booking(
            date=selected_date,
            time=selected_time.strftime('%H:%M'),
            service=form.service.data,
            user_id=current_user.id
        )
        db.session.add(new_booking)
        db.session.commit()

        msg = Message(
            subject="Masszázs foglalás visszaigazolása",
            recipients=[current_user.email],
            body=f"""Kedves {current_user.name}!

        Sikeresen lefoglaltad az alábbi időpontot:

        🗓 Dátum: {selected_date.strftime('%Y-%m-%d')}
        ⏰ Időpont: {selected_time.strftime('%H:%M')}
        💆 Szolgáltatás: {form.service.data}

        Köszönjük, hogy minket választottál!
        Üdvözlettel:
        Masszázs App
        """
        )
        mail.send(msg)
        flash('Sikeres foglalás!', "success")
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        for errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    return render_template(
        'booking.html',
        form=form,
        all_times=all_times_str,
        blocked_times=blocked_times,
        available_times=available_times
    )


@main.route('/booking/edit/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    """Létező időpont szerkesztése. Az elérhető időpontok
        újraszámítása történik."""
    current_booking = Booking.query.get_or_404(booking_id)

    if current_booking.user_id != current_user.id \
            and not current_user.is_admin:
        flash("Nincs jogosultságod módosítani ezt a foglalást.", "error")
        return redirect(url_for('main.profile'))

    form = BookingForm()
    available_get_service = MassageService.query.all()
    form.service.choices = [(s.name, s.name) for s in available_get_service]

    if request.method == 'GET' and 'date' \
            in request.args and request.args.get('date'):
        selected_date = datetime.strptime(
            request.args.get('date'), '%Y-%m-%d').date()
        form.date.data = selected_date
    else:
        selected_date = form.date.data or current_booking.date
        form.date.data = selected_date

    all_times = [
        (datetime.combine(
            selected_date, time(8, 0)) +
            timedelta(minutes=30 * i)).time()
        for i in range(25)
    ]
    all_times_str = [t.strftime('%H:%M') for t in all_times]

    bookings = Booking.query.filter_by(
        date=selected_date).filter(
            Booking.id != current_booking.id).all()

    blocked_set = set()
    for b in bookings:
        booked_time = datetime.strptime(b.time, "%H:%M").time()
        for offset in [-30, 0, 30]:
            blocked = (datetime.combine(selected_date, booked_time)
                       + timedelta(minutes=offset)).time()
            blocked_set.add(blocked)

    now = datetime.now().replace(second=0, microsecond=0)
    is_today = selected_date == now.date()

    blocked_times = [t.strftime('%H:%M') for t in blocked_set]
    available_times = [
        t.strftime('%H:%M') for t in all_times
        if t.strftime('%H:%M') not in blocked_times and
        (not is_today or datetime.combine(selected_date, t) > now)
    ]

    if form.validate_on_submit():
        selected_date = form.date.data
        selected_time = form.time.data
        selected_datetime = datetime.combine(selected_date, selected_time)

        if selected_datetime <= now:
            flash("Nem módosíthatsz múltbeli időpontra.", "error")
        elif selected_datetime.weekday() in [5, 6]:
            flash("Hétvégére nem lehet foglalni.", "error")
        else:
            if selected_date == current_booking.date and \
                selected_time.strftime('%H:%M') == current_booking.time and \
                    form.service.data == current_booking.service:
                flash("A foglalás adatai nem változtak.", "error")
                return redirect(url_for('main.profile'))
            times_to_check = [
                (selected_datetime - timedelta(minutes=30)).time(),
                selected_time,
                (selected_datetime + timedelta(minutes=30)).time()
            ]
            conflict = Booking.query.filter(
                Booking.date == selected_date,
                Booking.time.in_([t.strftime('%H:%M')
                                  for t in times_to_check]),
                Booking.id != current_booking.id
            ).first()

            if conflict:
                flash(
                    "Ez az időpont vagy annak ±30 perce már "
                    "foglalt.", "error")
            else:
                current_booking.date = selected_date
                current_booking.time = selected_time.strftime('%H:%M')
                current_booking.service = form.service.data
                db.session.commit()
                msg = Message(
                    subject="Masszázs foglalás módosítva",
                    recipients=[current_user.email],
                    body=f"""Kedves {current_user.name}!

                A foglalásodat sikeresen módosítottuk:

                🗓 Új dátum: {selected_date.strftime('%Y-%m-%d')}
                ⏰ Új időpont: {selected_time.strftime('%H:%M')}
                💆 Szolgáltatás: {form.service.data}

                Ha nem te módosítottad, kérjük, vedd fel velünk a kapcsolatot!

                Üdvözlettel:
                Masszázs App
                """
                )
                mail.send(msg)
                flash('Foglalás módosítva.', "success")
                return redirect(url_for('main.profile'))

    return render_template(
        'booking.html',
        form=form,
        edit=True,
        all_times=all_times_str,
        blocked_times=blocked_times,
        available_times=available_times
    )


@main.route('/booking/delete/<int:booking_id>')
@login_required
def delete_booking(booking_id):
    """Foglalás törlése az adatbázisból, jogosultság-ellenőrzéssel."""
    current_booking = Booking.query.get_or_404(booking_id)

    if current_booking.user_id != current_user.id \
            and not current_user.is_admin:
        flash("Nincs jogosultságod törölni ezt a foglalást.", "error")
        return redirect(url_for('main.profile'))

    db.session.delete(current_booking)
    db.session.commit()
    flash('Foglalás törölve.', "success")
    if current_user.is_admin:
        return redirect(url_for('main.admin'))
    return redirect(url_for('main.profile'))


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profiladatok megtekintése és szerkesztése, valamint
        múltbeli foglalások megjelenítése."""
    form = ProfileUpdateForm(obj=current_user)

    if form.validate_on_submit():
        if not check_password_hash(current_user.password,
                                   form.current_password.data):
            flash("Hibás jelszó. A módosítás nem engedélyezett.", "error")
            return redirect(url_for('main.profile'))

        current_user.name = form.name.data
        current_user.email = form.email.data

        if form.new_password.data:
            current_user.password = generate_password_hash(
                form.new_password.data)

        db.session.commit()
        flash("Profil sikeresen frissítve.", "success")
        return redirect(url_for('main.profile'))

    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html',
                           profile_form=form, bookings=bookings)


@main.route('/logout')
@login_required
def logout():
    """Felhasználó kijelentkeztetése."""
    logout_user()
    flash('Sikeres kijelentkezés.', "success")
    return redirect(url_for('main.index'))


@main.route('/admin')
@login_required
def admin():
    """Admin felület: felhasználók, szolgáltatások,
        foglalások és statisztikák kezelése."""
    if not current_user.is_admin:
        flash("Nincs jogosultságod az admin felülethez.", "error")
        return redirect(url_for('main.index'))

    users = User.query.all()
    services = MassageService.query.all()
    bookings = Booking.query.all()

    service_form = ServiceForm()

    service_chart_data = db.session.query(
        Booking.service, func.count(Booking.id)
    ).group_by(Booking.service).all()

    weekday_distribution = db.session.query(
        func.strftime('%w', Booking.date),
        func.count(Booking.id)
    ).group_by(func.strftime('%w', Booking.date)).all()

    weekday_map = ['Vasárnap', 'Hétfő', 'Kedd', 'Szerda',
                   'Csütörtök', 'Péntek', 'Szombat']
    weekday_chart_data = [(weekday_map[int(day)], count)
                          for day, count in weekday_distribution]

    return render_template(
        'admin.html',
        users=users,
        services=services,
        bookings=bookings,
        service_form=service_form,
        service_chart_data=service_chart_data,
        weekday_chart_data=weekday_chart_data
    )


@main.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    """Felhasználó törlése admin jogosultsággal.
        Admin felhasználó nem törölhető."""
    if not current_user.is_admin:
        flash("Nincs jogosultságod a felhasználók kezeléséhez.", "error")
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    if user.is_admin:
        flash("Admin felhasználót nem lehet törölni.", "error")
    else:
        Booking.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash("Felhasználó törölve.", "success")

    return redirect(url_for('main.admin'))


UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@main.route('/admin/add_service', methods=['POST'])
@login_required
def add_service():
    """Új szolgáltatás hozzáadása admin jogosultsággal, képfeltöltéssel."""
    if not current_user.is_admin:
        flash("Nincs jogosultságod szolgáltatást hozzáadni.", "error")
        return redirect(url_for('main.index'))

    form = ServiceForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(UPLOAD_FOLDER, filename))

        new_service = MassageService(
            name=form.name.data,
            description=form.description.data,
            price=float(form.price.data),
            image_filename=filename
        )
        db.session.add(new_service)
        db.session.commit()
        flash("Szolgáltatás hozzáadva.", "success")
    else:
        flash("Hibás adatok.", "error")

    return redirect(url_for('main.admin'))


@main.route('/admin/delete_service/<int:service_id>')
@login_required
def delete_service(service_id):
    """Szolgáltatás törlése admin jogosultsággal."""
    if not current_user.is_admin:
        flash("Nincs jogosultságod szolgáltatás törléséhez.", "error")
        return redirect(url_for('main.index'))

    service = MassageService.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash("Szolgáltatás törölve.", "success")
    return redirect(url_for('main.admin'))


@main.route('/admin/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    """Szolgáltatás adatainak módosítása admin jogosultsággal."""
    service = MassageService.query.get_or_404(service_id)
    form = ServiceForm(obj=service)

    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.price = float(form.price.data)

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(UPLOAD_FOLDER, filename))
            service.image_filename = filename

        db.session.commit()
        flash("Szolgáltatás frissítve.", "success")
        return redirect(url_for('main.admin'))

    return render_template('edit_service.html', form=form, service=service)


@main.route("/export_ics")
@login_required
def export_ics():
    """A felhasználó összes foglalását exportálja .ics (naptár) formátumban."""
    calendar = Calendar()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    for b in bookings:
        event = Event()
        event.name = b.service
        event.begin = f"{b.date} {b.time}"
        event.duration = {"minutes": 30}
        event.description = "Masszázs időpont"
        calendar.events.add(event)

    ics_file = str(calendar)
    return Response(
        ics_file,
        mimetype="text/calendar",
        headers={"Content-Disposition":
                 "attachment;filename=masszazs_foglalasok.ics"}
    )


@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Profiladatok frissítése külön POST route-on keresztül,
        jelszóellenőrzéssel."""
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash(
                "Hibás jelszó. "
                "A módosításhoz hitelesítés szükséges.", "error")
        else:
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Profil adatok sikeresen frissítve!", "success")
    return redirect(url_for('main.profile'))


@main.route('/services')
def services():
    """Szolgáltatások oldala, ahol az elérhető szolgáltatások
        listázva vannak."""
    services = MassageService.query.all()
    return render_template('services.html', services=services)


@main.route('/api/free_slots')
def free_slots():
    """API végpont, amely visszaadja a következő 14 nap
        szabad félórás időpontjait JSON formátumban."""
    today = date.today()
    upcoming_days = [today + timedelta(days=i) for i in range(14)]
    events = []

    for day in upcoming_days:
        if day.weekday() in [5, 6]:
            continue

        bookings = Booking.query.filter_by(date=day).all()

        blocked_times = set()

        for b in bookings:
            if isinstance(b.time, str):
                t = datetime.strptime(b.time[:5], '%H:%M').time()
            else:
                t = b.time

            dt = datetime.combine(day, t)

            for offset in [-30, 0, 30]:
                blocked_dt = dt + timedelta(minutes=offset)
                blocked_time_str = blocked_dt.time().strftime('%H:%M')
                blocked_times.add(blocked_time_str)

        for i in range(25):
            t = (datetime.combine(day, time(8, 0))
                 + timedelta(minutes=i * 30)).time()
            t_str = t.strftime('%H:%M')

            if t_str in blocked_times:
                continue

            events.append({
                "title": f"Szabad időpont: {t_str}",
                "start": f"{day}T{t_str}",
                "url": url_for('main.booking',
                               date=day.isoformat(),
                               time=t_str)
            })

    return jsonify(events)
