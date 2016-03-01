# -*- coding: utf8 -*-

from sys import exc_info
from config import LOGGER

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import coreApp, db, lm
from .forms import LoginForm, LostPasswdForm, EditUserForm, AddUserForm, AddSpendingForm
from .models import User, Spending

from functools import wraps
from babel.dates import format_date, datetime
from sqlalchemy import desc


# THIS FUNCTION SHOULD BE A STATIC_METHOD OF SPENDING() CLASS!
def addBill(s_type, s_label, s_total, s_payer_id, s_user_ids):
    """
        create a Spending in the database.
          1) create the Spending model and fill its attributes except parts
          2) estimate parts and add them to our Spending
          3) adjust balance for each User with this parts
          4) until no errors: add all of this in the database
    """
    try:
        bill = Spending()
        bill.timestamp = datetime.utcnow()
        bill.s_type = s_type
        bill.label = s_label
        bill.total = s_total
        bill.payer_id = s_payer_id
        db.session.add(bill)

        db.session.query(User).get(s_payer_id).given_money += float(bill.total)
        
        tmp_parts = bill.computeParts(db.session, len(s_user_ids))
        user_parts = []
        for idx, i in enumerate(tmp_parts):
            db.session.add(
                Spending.Part(
                    spending=bill,
                    total=i, # == tmp_parts[idx],
                    user_id=s_user_ids[idx]
                )
            )
            user_parts.append([s_user_ids[idx], i])
        
        for user_id, user_bill in user_parts:
            db.session.query(User).get(user_id).borrowed_money += user_bill

        db.session.commit()
        return 1
    except:
        db.session.rollback()
        LOGGER.p_log(u'impossible d\'ajouter la dépense', exception=exc_info())     
        return 0


def delBill():
    return 1







app_name = coreApp.config['APP_NAME']

### BEGIN: DECORATORS ###
@coreApp.before_request # any method that are decorated with before_request will run before the view method each time a request is received
def before_request():
    g.user = current_user # GLOBAL var to simplify access, notably in templates (global current_user is set by Flask)
    if g.user.is_authenticated:
        g.user.last_connection = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    #cookies initialization
        if 'spends_page' in session:
            spends_page = session['spends_page']
        else:
            session['spends_page'] = 'depenses' #default spendings page

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        "login_required Flask's method overriding to remove non-french (english) flashes"
        if not g.user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


#fonction inutilisée et jamais appelée ! pourquoi ? :o
@coreApp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', app_name=app_name), 404

@coreApp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', app_name=app_name), 500

### END: DECORATORS ###



@coreApp.route('/')
@coreApp.route('/index')
@login_required
def index():
    print g.user
    return render_template('index.html', menu_not_collapsed=False, app_name=app_name)


@coreApp.route('/thewall')
@login_required
def thewall():
    return render_template('thewall.html', app_name=app_name)



### BEGIN: USER ACCESS ###
@coreApp.route('/login', methods=['GET', 'POST'])
def login():
    # if g.user is not None and not g.user.is_anonymous():
    if g.user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            #session['remember_me'] = form.remember_me.data
            return try_login(form.email.data, form.password.data)
            
        else:
            for errors in form.errors.values():
                for error in errors:
                    flash(error)
                    print error
            return render_template('login.html', form=form, app_name=app_name)

@lm.user_loader
def loadUser(id):  #NOTE: user ids in Flask-Login are always unicode strings
    "Flask useful method"
    #really? I think this method is useless (Bat)
    return User.query.get(int(id))

def try_login(email, password):
# TODO: investigate on this method, optimize
    print 'on passe dans try_login'
    user = User.query.filter_by(email = email).first()
    if user == None:
        print 'user is NONE'
        flash(u'mmh... mauvaise adresse mail !')
        return redirect(url_for('index'))
    elif user.password == password:
        print 'mail et password concordent'
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
    else:
        flash(u'mauvais mot de passe')
        print 'WRONG PASSWORD'
        return redirect(url_for('index'))
    print 'on redirige'
    return redirect(request.args.get('next') or url_for('index'))


@coreApp.route('/logout')
def logout():
    logout_user()
    session.pop('spends_page', None)
    return redirect(url_for('index'))



@coreApp.route('/lostPasswd', methods=['GET', 'POST'])
def lostPasswd():
    "password recovery webpage"
    form = LostPasswdForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None:
            user.getPasswd()
            flash(u"nouveau mot de passe envoyé, vérifie tes mails !")
        else:
            flash(u"je ne connais pas ce mail, désolé !")
        return redirect(url_for('lostPasswd'))

        
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error)
                print error
        return render_template('lostPasswd.html', form=form, app_name=app_name)



@coreApp.route('/getUser/<email>', methods=['GET', 'POST'])
@login_required
def getUser(email):
    user = User.query.filter_by(email=email).first()
    form = EditUserForm(g.user.email)
    if user is None:
        flash('Utilisateur %s introuvable' % email)
        users = User.query.order_by('last_connection desc').all()
        return render_template('getUsers.html', users=users, app_name=app_name)
    else:
        if form.validate_on_submit():
            g.user.firstname = form.firstname.data
            g.user.email = form.email.data
            g.user.timezone = form.timezone.data
            db.session.add(g.user)
            db.session.commit()
            flash(u'tes modifs\' sont bien enregistrées')
        else:
            form.firstname.data = g.user.firstname
            form.email.data = g.user.email
            form.timezone.data = g.user.timezone
        return render_template('getUser.html', app_name=app_name, user=user, form=form)


@coreApp.route('/getUsers')
@login_required
def getUsers():
    #pour afficher les lucioles selon l'ordre de dernière connection :
    users = User.query.order_by('last_connection desc').all()
    return render_template('getUsers.html', app_name=app_name, users=users)

@coreApp.route('/addUser', methods=['GET', 'POST'])
@login_required
def addUser():
    """cette méthode devrait ptet etre une méthode static de la classe User mmh ?
    """
    #print current_user.balance.user_id
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            firstname=form.firstname.data,
            timezone=form.timezone.data
        )
        db.session.add(user)
        db.session.commit()
        print user.id
        u_balance = Balance(user_id=user.id)
        db.session.add(u_balance)
        db.session.commit()
        print ''
        print ''
        print ''
        print u_balance.id
        user.balance = u_balance.id
        db.session.commit()
        flash(u'utilisateur enregistré !')
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error)
    return render_template('addUser.html',
        app_name=app_name,
        form=form
    )





### END: USER ACCESS ###




### BEGIN: COMPTES ##
@coreApp.route('/comptes')
def comptesBis():
    return redirect(url_for('comptes', spends_page='depenses'))
@coreApp.route('/comptes/')
def comptes2Bis():
    return redirect(url_for('comptes', spends_page='depenses'))

@coreApp.route('/comptes/<spends_page>', methods=['GET', 'POST'])
@login_required
def comptes(spends_page):
    """
        Todo:
            - only print entries for the current_user
            - régler cette histoire de dropdown-menu (voir dans ajoutDepense.html la différence entre les catégories et le choix de payeur_id)
                en gros l'un (catégories) est joli mais pas complet et utilise bootstrap à l'arrache, l'autre (payeur) utilise flask mais est un peu moche
                voir la doc là : http://wtforms.simplecodes.com/docs/0.6/fields.html
                et là : http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html
    """

    # delete a spending and his parts
    if spends_page.split("_")[0] == "spendingdel":
        Spending.query.filter_by(
            id=int(spends_page.split("_")[1])
        ).delete()
        # db.session.query(Spending).get(
        #     id=int(spends_page.split("_")[1])
        # ).delete()
        parts = Spending.Part.query.filter_by(
            spending_id=int(spends_page.split("_")[1])
            ).delete()
        db.session.commit()
        spends_page="depenses"

    session['spends_page'] = spends_page


    # add a spending to the database
    if spends_page == 'ajoutDepense':
        form = AddSpendingForm()
        users = [(user.id, user.getName(user.id)) for user in User.query.order_by('id')]
        form.payer_id.choices = users
        form.bill_user_ids.choices = users
        if form.validate_on_submit():
            if addBill(
                form.s_type.data,
                form.label.data,
                form.total.data,
                form.payer_id.data,
                form.bill_user_ids.data
            ):
                flash(u'la dépense a bien été ajoutée')
                return redirect(url_for('comptes', spends_page='depenses'))
            else:
                flash(u'impossible d\'ajouter la dépense')
                return redirect(url_for('comptes', spends_page='depenses'))
        else:
            for errors in form.errors.values():
                for error in errors:
                    flash(error)
                    print error

            # query on spending.types
            types = []
            for ttype in Spending.Type.query.all():
                types.append(ttype.name)

            # query on spending.users
            """
            users = User.query.all()
            c_users = []
            for user in users:
                c_users.append((user.id, str(User.getName(user.id))))
            """

            return render_template(
                'comptes.html',
                app_name=app_name,
                spends_page=spends_page,
                form=form,
                types=types,
                #users=c_users
            )

    # list all spendings from the database
    if spends_page == 'depenses':
        #print 'DEL', request.form['del_spending']
        payers = {}
        times = {}
        my_parts = {}
        payer_ids = {}
        spendings = Spending.query.order_by(desc('timestamp')).all()

        for spending in spendings:
            from pprint import pprint
            pprint(spending)
            times[spending.id] = spending.getDate(current_user)
            payers[spending.id] = User.getName(spending.payer_id)
            my_parts[spending.id] = Spending.getPart(spending, current_user.id)
        return render_template('comptes.html',
            app_name=app_name,
            spends_page=spends_page,
            spendings=spendings,
            times=times,
            payers=payers,
            my_parts=my_parts,
            my_rows=g.user.spends.all()
        )

    # list all repayments
    if spends_page == 'remboursements':
        return render_template(
            'comptes.html',
            app_name=app_name,
            spends_page=spends_page,
        )

    # list users' balances
    if spends_page == 'balances':
        users = User.query.order_by('user_id').all()
        return render_template(
            'comptes.html',
            app_name=app_name,
            spends_page=spends_page,
            users=users
        )

    # else
    return redirect(url_for(
        'comptes',
        app_name=app_name,
        spends_page='depenses'
    ))


### END: COMPTES ###



### BEGIN: CALENDRIER ###
@coreApp.route('/calendrier')
@login_required
def calendrier():
    return 'calendrier'

### CALENDRIER ###