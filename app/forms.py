# -*- coding: utf8 -*-
import math

from flask_wtf import FlaskForm as Form
from wtforms import widgets, StringField, PasswordField, DateField, SelectMultipleField, SelectField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, required, optional

from app.models import User
from babel.dates import datetime


class LoginForm(Form):
    # TODO: dans cette fonction, j'avais prévu de faire de l'autocomplétion de lucioles, et de filer un mot de passe si inconnu. peut-être pas pour la CCC mais au moins pour theWall, qui ne concerne(ra) QUE mes lucioles :-)
    email = StringField('Email', [DataRequired(u"si tu me passes pas ton mail ça va pas le faire :-)")])
    password = PasswordField('Mot de passe', [DataRequired(u"eh, tu dois entrer ton mot de passe !")])
    # remember_me = BooleanField('remember_me', default=False)


class LostPasswdForm(Form):
    email = StringField('Email', [DataRequired(u"eh, je veux bien chercher ton mot de passe mais il me faut au moins ton mail !")])


class EditUserForm(Form):
    email = StringField('email', validators=[DataRequired()])
    firstname = StringField('firstname', validators=[DataRequired()])
    timezone = StringField('timezone', validators=[DataRequired()])
    new_password = PasswordField('new_password', [optional()], default='')

    def __init__(self, original_mail, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_mail = original_mail

    def validate(self):
        flag_mail = False
        if not Form.validate(self):
            return False

        if self.email.data == self.original_mail:
            flag_mail = True
        else:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                self.email.errors.append(u'ce mail est déjà pris !')
                flag_mail = False
            else:
                flag_mail = True

        if not flag_mail:
            return False

        if self.new_password.data == '':
            return True
        else:
            # implement some other checks on this new password
            print(len(self.new_password.data))
            if len(self.new_password.data) < 8:
                self.new_password.errors.append(u'ton mot de passe doit contenir au moins 8 caractères !')
                return False
            return True


class AddUserForm(Form):
    """
        ToDo:
        les validateurs de ce formulaire ne sont pas implémentés !
            > par exemple check que l'user (mail) n'existe pas déjà...
            > et pis le mot de passe là en clair ça craint à mort !
    """
    email = StringField(u'Email', [required('il nous faut entrer ton email !')])
    password = PasswordField(u'Mot de passe :', [required('il nous faut un mot de passe !')])
    firstname = StringField(u'Nom', [optional()])
    timezone = StringField(u'Timezone', [optional()], default='fr_FR')
    submit = SubmitField(u"Ajouter l'utilisateur")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SpendingForm(Form):
    label = StringField(u'Titre', validators=[DataRequired(u"t'as oublié le titre !")])
    comment = TextAreaField(u'Description')
    total = StringField(u'Montant', validators=[DataRequired(u"le montant est absent, ou n'est pas correct.")])
    s_date = DateField(
        u'Date',
        [required(u"la date ?")],
        format="%d/%m/%Y",
        default=datetime.today
    )
    s_type = HiddenField(u'Catégorie', validators=[DataRequired(u"la catégorie ?")])
    payer_id = SelectField(u'Qui a payé ?', coerce=int)
    bill_user_ids = MultiCheckboxField(u'Pour qui ?')
    submit = SubmitField(u"Enregistrer la dépense")

    def validate(self):
        if self.bill_user_ids.data:
            for idx, data in enumerate(self.bill_user_ids.data):
                self.bill_user_ids.data[idx] = int(data)
        if not Form.validate(self):
            return False
        else:
            if not self.bill_user_ids.data:
                self.bill_user_ids.errors.append(u"à qui profite cette dépense ?")
                return False
            self.total.data = self.total.data.replace(" ", "").replace(",", ".")
            if float(self.total.data) <= 0:
                self.total.errors.append(u"désolé, mais une dépense d'un montant nul ou négatif, ça n'existe pas !")
                return False
            if len(self.total.data.split('.')) > 1:  # there are centimes: how many?
                if len(self.total.data.split('.')[1]) > 2:
                    self.total.errors.append(u't\'es sûr de tes centimes là ? petit chenapan !')
                    return False
            return True
