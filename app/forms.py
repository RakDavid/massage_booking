"""Űrlapok definiálása a Flask alkalmazáshoz."""

from datetime import date, datetime, time

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, SubmitField,
    DateField, TimeField, SelectField,
    TextAreaField, DecimalField
)
from wtforms.validators import (
    InputRequired, Email, Length, EqualTo,
    DataRequired, ValidationError, NumberRange, Optional
)


class RegisterForm(FlaskForm):
    """Felhasználói regisztrációs űrlap."""
    name = StringField('Név', validators=[
        InputRequired(), Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        InputRequired(), Email()
    ])
    password = PasswordField('Jelszó', validators=[
        InputRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Jelszó mégegyszer', validators=[
        InputRequired(), EqualTo('password')
    ])
    submit = SubmitField('Regisztráció')


class LoginForm(FlaskForm):
    """Bejelentkezési űrlap."""
    email = StringField('Email', validators=[
        InputRequired(), Email()
    ])
    password = PasswordField('Jelszó', validators=[
        InputRequired()
    ])
    submit = SubmitField('Bejelentkezés')


class BookingForm(FlaskForm):
    """Időpontfoglalási űrlap."""
    date = DateField('Dátum', validators=[
        DataRequired()
    ], format='%Y-%m-%d')
    time = TimeField('Időpont', validators=[
        DataRequired()
    ], format='%H:%M')
    service = SelectField('Szolgáltatás', choices=[], validators=[
        DataRequired()
    ])
    submit = SubmitField('Foglalás')

    def validate_date(self, field):
        """Múltbeli dátum ellenőrzése."""
        today = date.today()
        if field.data < today:
            raise ValidationError("Nem lehet múltbeli dátumot választani.")

    def validate_time(self, field):
        """Időintervallum és jelenidő ellenőrzése."""
        if self.date.data == date.today():
            now = datetime.now().time()
            if field.data <= now:
                raise ValidationError(
                    "Nem lehet a jelenlegi időpont előtt foglalni."
                )
        if not time(8, 0) <= field.data <= time(19, 30):
            raise ValidationError(
                "Csak 8:00 és 20:00 közötti időpontokra lehet "
                "foglalni félórás bontásban."
            )


class ServiceForm(FlaskForm):
    """Szolgáltatás hozzáadása vagy szerkesztése."""
    name = StringField('Név', validators=[
        DataRequired(), Length(max=100)
    ])
    description = TextAreaField('Leírás', validators=[
        DataRequired(), Length(max=500)
    ])
    price = DecimalField('Ár (Ft)', validators=[
        DataRequired(), NumberRange(min=0)
    ])
    image = FileField('Kép', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Csak képfájlok!')
    ])
    submit = SubmitField()


class ProfileUpdateForm(FlaskForm):
    """Profil frissítési űrlap."""
    name = StringField("Név", validators=[DataRequired()])
    email = StringField("Email", validators=[
        DataRequired(), Email()
    ])
    new_password = PasswordField("Új jelszó (opcionális)", validators=[
        Optional()
    ])
    current_password = PasswordField("Jelenlegi jelszó", validators=[
        DataRequired()
    ])
    submit = SubmitField("Mentés")
