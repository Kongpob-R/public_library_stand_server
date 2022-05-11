from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from flask_login import login_required, login_user, logout_user
from .models import User, Ereader
from . import db
import os

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    ereaders = Ereader.query.all()
    if request.method == 'GET':
        return render_template(
            'login.html',
            ereaders=ereaders
        )
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')
    ereaderuid = request.args.get('ereaderuid', default='', type=str)

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))
    if user.role == 'superuser':
        login_user(user)
        return redirect(url_for('main.dashboard'))
    allEreaderuid = []
    for ereader in ereaders:
        allEreaderuid.append(ereader.ereaderuid)
    if ereaderuid not in allEreaderuid:
        flash('Please check your E-reader devices UID and try again.')
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    user.ereaderuid = ereaderuid
    db.session.commit()
    login_user(user)
    return redirect(url_for('main.index'))


@auth.route('/callback.php')
def callback():
    authPageUrl = os.getenv('AUTH_PAGE_URL')
    token = request.args.get('token', default='', type=str)
    xsid = request.args.get('xsid', default='', type=str)
    result = request.args.get('result', default='', type=str)
    userInfo = request.args.get('userInfo', default='', type=str)
    username = userInfo.split('@')[0]
    user = User.query.filter_by(username=username)
    # if result failed
    if result == 'fail':
        return redirect(authPageUrl+'?'+'xsid='+xsid+'&'+'token='+token)
        # if token mismatch
    if token == os.getenv('TOKEN'):
        return redirect(authPageUrl+'?'+'xsid='+xsid+'&'+'token='+token)
        # if no user found
    if user.count() == 0:
        User.createuser(username=username, password=userInfo)
        db.session.commit()
    user = User.query.filter_by(username=username).first()
    user.ereaderuid = xsid
    db.session.commit()
    login_user(user)
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
