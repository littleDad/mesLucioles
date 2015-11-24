# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import coreApp, db, lm
from .forms import LoginForm, LostPasswdForm, EditUserForm
from .models import User, Spending

from functools import wraps
from datetime import datetime

### BEGIN: DECORATORS ###
@coreApp.before_request # any method that are decorated with before_request will run before the view method each time a request is received
def before_request():
    g.user = current_user # GLOBAL var to simplify access, notably in templates (global current_user is set by Flask)
    if not g.user.is_anonymous():
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
        if g.user.is_anonymous():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


#fonction inutilisée et jamais appelée ! pourquoi ? :o
@coreApp.errorhandler(404)
def not_found_error(error):
    return 'pas de ça chez nous ! (erreur 404)'

@coreApp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

### END: DECORATORS ###



@coreApp.route('/')
@coreApp.route('/index')
@login_required
def index():
    print g.user
    return render_template('index.html', menu_not_collapsed=True)


@coreApp.route('/thewall')
@login_required
def thewall():
    return render_template('thewall.html')



### BEGIN: USER ACCESS ###
@coreApp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and not g.user.is_anonymous():
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
            return render_template('login.html', form=form)

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
        return render_template('lostPasswd.html', form=form)



@coreApp.route('/getUser/<email>', methods=['GET', 'POST'])
@login_required
def getUser(email):
    user = User.query.filter_by(email=email).first()
    form = EditUserForm(g.user.email)
    if user is None:
        flash('Utilisateur %s introuvable' % email)
        users = User.query.order_by('last_connection desc').all()
        return render_template('getUsers.html', users=users)
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
        return render_template('getUser.html', user=user, form=form)


@coreApp.route('/getUsers')
@login_required
def getUsers():
    #pour afficher les lucioles selon l'ordre de dernière connection :
    users = User.query.order_by('last_connection desc').all()
    return render_template('getUsers.html', users=users)

### END: USER ACCESS ###




### BEGIN: COMPTES ##
@coreApp.route('/comptes/<spends_page>')
def comptes(spends_page):
    session['spends_page'] = spends_page
    rows = []
    if spends_page == 'depenses':
        rows = Spending.query.order_by('timestamp').all()
        for row in rows:
            print row
    return render_template('comptes.html',
                           spends_page=spends_page,
                           rows=rows,
                           my_rows=g.user.spends.all())

@coreApp.route('/comptes/ajoutDepense', methods=['GET', 'POST'])
def ajoutDepense():
    "add a spend to the database"
    form = AddSpendForm()
    if form.validate_on_submit():
        newSpend = Spending()
        newSpend.type = form.type.data
        newSpend.label = form.label.data
        newSpend.total = form.total.data
        newSpend.timestamp = form.timestamp.data
        newSpend.payeur_id = form.payeur_id.data
        newSpend.timestamp = form.timestamp.data
        db.session.add(newSpend)
        db.session.commit()
        flash(u'la dépense a bien été ajoutée')
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error)
                print error
        return render_template('ajoutDepense.html', form=form)

    return url_for('comptes', spends_page=session['spends_page'])


### END: COMPTES ###



### BEGIN: CALENDRIER ###
@coreApp.route('/calendrier')
def calendrier():
    return 'calendrier'

### CALENDRIER ###