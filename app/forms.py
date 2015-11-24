# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, FloatField, TextField, PasswordField
from wtforms.validators import DataRequired

from app.models import User


class LoginForm(Form):
#TODO: dans cette fonction, j'avais prévu de faire de l'autocomplétion de lucioles, et de filer un mot de passe si inconnu. peut-être pas pour la CCC mais au moins pour theWall, qui ne concerne(ra) QUE mes lucioles :-)
    email = StringField('Email', [DataRequired(u"si tu me passes pas ton mail ça va pas le faire :-)")])
    password = PasswordField('Mot de passe', [DataRequired(u"eh, tu dois entrer ton mot de passe !")])
    #remember_me = BooleanField('remember_me', default=False)

class LostPasswdForm(Form):
    email = StringField('Email', [DataRequired(u"eh, je veux bien chercher ton mot de passe mais il me faut au moins ton mail !")])


class EditUserForm(Form):
    email = StringField('email', validators=[DataRequired()])
    firstname = StringField('firstname', validators=[DataRequired()])
    timezone = StringField('timezone', validators=[DataRequired()])

    def __init__(self, original_mail, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_mail = original_mail

    def validate(self):
        if not Form.validate(self):
            return False
        elif self.email.data == self.original_mail:
            return True
        else:
            user = User.query.filter_by(email=self.email.data).first()
            if user != None:
                self.email.errors.append(u'ce mail est déjà pris !')
                return False
            else:
                return True
            

class AddSpendForm(Form):
    type = StringField('type', validators=[DataRequired()])
    label = StringField('Titre', validators=[DataRequired()])
    total = FloatField('Montant', validators=[DataRequired()])
    timestamp = StringField('Date', validators=[DataRequired()])
    payeur_id = StringField('Payeur', validators=[DataRequired()])
    #autres