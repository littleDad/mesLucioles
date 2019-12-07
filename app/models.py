# -*- coding: utf8 -*-

from decimal import Decimal as dec, getcontext
from random import shuffle

from babel.dates import format_date
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from config import \
    LOGGER  # pour le support de la recherche dans les factures, voir : https://github.com/miguelgrinberg/microblog/blob/master/app/models.py


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    firstname = db.Column(db.String(64), index=True, default=u'inconnu(e)')
    last_connection = db.Column(db.DateTime)
    timezone = db.Column(db.String(5), default='fr_FR')
    # given_money = db.Column(db.Float(10), default=0)
    # borrowed_money = db.Column(db.Float(10), default=0)
    spends = db.relationship('Spending', backref='payer', lazy='dynamic') # so we can use Spending.payer to get the User instance that created a Spending

    @staticmethod
    def useless_method():
        "I am static, that's why you can call me without any user (self) parameter !"
        print('i am an useless static method')

    def avatar(self):
        return 'chemin-vers-l-image'

    def is_authenticated(self):
        "should just return True unless the object represents a user that should not be allowed to authenticate for some reason"
        print('AUTHENTICATED')
        print('user_id:', self.get_id())
        return True 

    def is_active(self):
    #TODO: useless function?
        "should return True for users unless they are inactive, for example because they have been banned"
        return True
    def is_anonymous(self):
    #TODO: useless function?
        "should return True only for fake users that are not supposed to log in to the system"
        return False

    def get_id(self):
        "should return a unique identifier for the user, in unicode format"
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        print(self)
        return check_password_hash(self.password, password)

    def getPasswd(self):
        "envoie un mail avec un nouveau mot de passe"
        #à implémenter
        return True
        #si ça ne fonctionne pas
        return False

    def getLastConnection(self):
        """return user (self) lastConnection attribute according to user timezone"""
        return format_date(self.last_connection, locale=self.timezone)

    def __repr__(self):
        return '<User %r> (%r)' % (self.email, self.firstname)

    def get_balance(self):
        return self.balance

    # def edit_money(self, m_type, order, amount):
    #     exec('self.'+str(m_type)+str(order)+'= '+str(amount))
    #     exec('print(self.'+str(m_type)+')')

    def getName(self):
        user = User.query.filter_by(id=self.id).first().firstname
        if user == "inconnu(e)":
            return User.query.filter_by(id=self.id).first().email
        return user
    @staticmethod
    def getNameStatic(user_id):
        user = User.query.filter_by(id=user_id).first().firstname
        if user == "inconnu(e)":
            return User.query.filter_by(id=user_id).first().email
        return user

    def get_total_paid(self):
        total_paid = db.session.query(func.sum(Spending.total)).filter_by(payer_id=self.id).all()[0][0]
        if total_paid is None:
            total_paid = 0.0
        return float("{0:.2f}".format(
            total_paid
        ))

    def get_total_paid_without_transfers(self):
        total_paid_without_transfers = db.session.query(
            func.sum(Spending.total)).filter_by(payer_id=self.id).filter(Spending.s_type != 'Virement').all()[0][0]
        if total_paid_without_transfers is None:
            total_paid_without_transfers = 0.0
        return float("{0:.2f}".format(
            total_paid_without_transfers
        ))

    def get_transfers_total(self):
        trasnsfers_total_amount = db.session.query(
            func.sum(Spending.total)).filter_by(payer_id=self.id, s_type='Virement').all()[0][0]
        if trasnsfers_total_amount == None:
            trasnsfers_total_amount = 0.0
        return float("{0:.2f}".format(
            trasnsfers_total_amount
        ))

    def getBorrowed_money(self):
        borrowed_money = db.session.query(
            func.sum(Spending.Part.total)
        ).filter_by(user_id=self.id).all()[0][0]
        if borrowed_money == None:
            borrowed_money = 0.0
        return float("{0:.2f}".format(
            borrowed_money
        ))
    def getBalance(self):
        return float("{0:.2f}".format(
            self.get_total_paid() - self.getBorrowed_money()
        ))


class WallMessage(db.Model):
    """ (EN CHANTIER)
        manager du mur principal de messages.
        doit être unique (implémenter template singleton)

    """
    id = db.Column(db.Integer, primary_key = True)




class Spending(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    # attention, à l'utilisation : enregistrer le temps UTC, parce qu'on a potentiellement des users du monde entier !
    timestamp = db.Column(db.DateTime)  # addition in the database date
    s_date = db.Column(db.DateTime)  # date from the real world
    s_type = db.Column(db.String(30)) # maybe an enumerate type in the future?
    label = db.Column(db.String(50))
    total = db.Column(db.Float(10))
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parts = db.relationship('Part', backref='spending', lazy='dynamic')
    comment = db.Column(db.String(400))

    def __repr__(self):
        return '<Dépense %r (n°%r) payer:%r>' % (self.label, self.id, self.payer_id)

    def getDate(self, user):
        """return spending (self) bought date attribute according to user timezone"""
        return format_date(self.s_date, "d MMM", locale=user.timezone)

    def computeParts(self, c_session, len_user_ids):
        """divide a spending into money parts for users.
            return a list of (user, to_pay) couples
        """
        def makeParts(value, nb_parts, spending_name, spending_time):
            """make nb_parts parts with the value.
            if centimes left, we allocate these lost ones to a random user. sometimes
                it's positive numbers, sometimes not!
            my priority was to NOT have lost centimes.

            note: all the computation deals with integer by *100 at the beginning and /100 at the end to save our souls
            from computers floating madness!
            """
            getcontext().prec = 6
            int_value_x_100 = int(dec(value) * 100)  # let's work with integer

            parts = [int_value_x_100 // nb_parts] * nb_parts
            left_centimes = int_value_x_100 % nb_parts
            while left_centimes > 0:
                for idx, part in enumerate(parts):
                    if left_centimes > 0:
                        parts[idx] += 1
                        left_centimes -= 1

            parts = [part / 100 for part in parts]  # go back to float numbers
            shuffle(parts)  # because expensive amount are always at the beginning, let's shuffle this!

            # any error is logged. because money is money. no jokes!
            if float(value) != float(sum(parts)):
                LOGGER.p_log('error in adding a spending', level='warning')
                LOGGER.p_log('spending_time: ' + str(spending_time), blank=True)
                LOGGER.p_log('value: ' + str(value), blank=True)
                LOGGER.p_log('sum: ' + str(sum(parts)), blank=True)
                LOGGER.p_log('parts: ' + str(parts), blank=True)
            return parts

        parts = makeParts(self.total, len_user_ids, self.label, self.timestamp)
        return parts

    @staticmethod
    def getPart(Spending, user_id):
        for part in Spending.parts:
            if part.user_id == user_id:
                return part.total
        return 0  # this user_id doesn't have to pay this bill

    class Part(db.Model): # Part.spending doit pouvoir récupérr le spending
        id = db.Column(db.Integer, primary_key = True)
        spending_id = db.Column(db.Integer, db.ForeignKey('spending.id'))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        total = db.Column(db.Float(10))

    class Type(db.Model):
        name = db.Column(db.String(30), primary_key = True)
