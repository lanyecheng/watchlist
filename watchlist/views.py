#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 视图函数
import arrow
import os
from flask import render_template, request, url_for, redirect, flash, send_from_directory, g, abort
from flask_login import login_user, login_required, logout_user, current_user
from os.path import join, exists, basename
from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.data_record import insert_record, get_records, delete_record
from xmind2case.xmind2htp import xmind_to_htp_preview, xmind_to_htp_xlsx_file
from xmind2case.utils import get_xmind_testsuites


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year) != 4 or len(title) > 60:
            # 显示错误提示
            flash('Invalid input.')
            # 重定向回主页
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year or len(year) != 4 or len(title) > 60:
            # 显示错误提示
            flash('Invalid input.')
            # 重定向回主页
            return redirect(url_for('index'))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/test')
def test():
    return render_template('test.html')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def save_file(file):
    if file and allowed_file(file.filename):
        filename = file.filename
        upload_to = join(app.config['UPLOAD_FOLDER'], filename)
        if exists(upload_to):
            filename = '{}_{}.xmind'.format(filename[:-6], arrow.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        file.save(upload_to)
        insert_record(filename)
        return filename


def delete_row(filename, record_id):
    """数据库逻辑删除"""
    xmind_file = join(app.config['UPLOAD_FOLDER'], filename)
    htp_file = join(app.config['UPLOAD_FOLDER'], filename[:-5] + 'xls')
    for f in [xmind_file, htp_file]:
        if exists(f):
            os.remove(f)
    delete_record(record_id)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    g.invalid_files = []
    g.filename = None
    g.error = None

    if request.method == 'POST':
        file = request.files['file']

        g.filename = save_file(file)
        # verify_uploaded_files([file])
    if g.filename:
        return redirect(url_for('preview', filename=g.filename))
    else:
        return render_template('upload.html', records=list(get_records()))


@app.route('/preview/<filename>')
def preview(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)
    if not exists(full_path):
        abort(404)

    testsuites = get_xmind_testsuites(full_path)
    suite_count = 0
    for suite in testsuites:
        suite_count += len(suite.sub_suites)

    testcases = xmind_to_htp_preview(full_path)
    return render_template('preview.html', name=filename, suite=testcases, suite_count=suite_count)


@app.route('/delete_file/<filename>/<int:record_id>')
def delete_file(filename, record_id):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)
    if not exists(full_path):
        abort(404)
    else:
        delete_row(filename, record_id)
    return redirect(url_for('upload'))


@app.route('/to/htp/<filename>')
def download_xmind_htp(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)
    if not exists(full_path):
        abort(404)
    htp_file = xmind_to_htp_xlsx_file(full_path)
    filename = basename(htp_file)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
