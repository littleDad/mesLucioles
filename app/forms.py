# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import widgets, StringField, BooleanField, FloatField, TextField, PasswordField, DateField, SelectMultipleField, SelectField, FormField, SubmitField, HiddenField, FieldList, IntegerField
from wtforms.validators import DataRequired, required, optional

from app.models import User
from babel.dates import datetime


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
class AddSpendingForm(Form):
    label = StringField(u'Titre', validators=[DataRequired(u"t'as oublié le titre !")])
    total = StringField(u'Montant', validators=[DataRequired(u"le montant est absent, ou n'est pas correct.")])
    date = DateField(
        u'Date',
        [required(u"la date ?")],
        format="%d/%m/%Y",
        default=datetime.today
    )
    s_type = HiddenField(u'Catégorie', validators=[DataRequired(u"la catégorie ?")])
    payer_id = SelectField(u'Qui a payé ?', coerce=int)
    bill_user_ids = MultiCheckboxField(u'Pour qui ?')
    submit = SubmitField(u"Ajouter la dépense")
    
    
    def validate(self):
        if (self.bill_user_ids.data != []):
            for idx, data in enumerate(self.bill_user_ids.data):
                self.bill_user_ids.data[idx] = int(data)
        if not Form.validate(self):
            return False
        else:
            if (self.bill_user_ids.data == []):
                self.bill_user_ids.errors.append(u"à qui profite cette dépense ?")
                return False
            total = (self.total.data).replace(" ","").replace(",",".")
            total = float(total)
            if len(str(total - int(total))) > 4:  # how many centimes?
                self.total.errors.append(u't\'es sûr de tes centimes là ? petit chenapan !')
                return False
            return True

