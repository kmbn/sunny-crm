import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, redirect, url_for, abort, \
    render_template, flash
from datetime import datetime
import json
from .forms import AddContactForm, AddCheckinForm, AddUpdateForm, \
    QuickNavForm, EditContactNameForm, EditNoteForm, EditCheckinForm, \
    RingTheBellForm, EditContactForm
from .parse import *
from . import app
from .db import get_db
from .mail import send_email
from .decorators import login_required


@app.route('/', methods=['GET', 'POST'])
def main_view():
    if session.get('logged_in'):
        current_user = session.get('current_user')
        quick_nav = QuickNavForm()
        # Do quicknav
        today = datetime.utcnow().date()
        db = get_db()
        # Get agenda
        cur = db.execute('select contacts.name, contacts.cid, \
            contacts.next_action, updates.id from contacts \
            join updates on contacts.id = updates.contact_id \
            where contacts.creator_id = ? and contacts.next_checkin <= ? \
            group by contacts.cid order by updates.id asc', \
            (current_user, today))
        agenda = cur.fetchall()
        # Get progress report
        cur = db.execute('select count(id) from contacts \
            where creator_id = ? and created_on = ?', (current_user, today))
        new_contacts = cur.fetchone()
        cur = db.execute('select count(id) from updates \
            where creator_id = ? and created_on = ?', (current_user, today))
        new_updates = cur.fetchone()
        if new_updates[0] != None:
            new_updates = new_updates[0] - new_contacts[0]
        # Get last five updates
        cur = db.execute('select updates.description, updates.created_on, \
            contacts.name, contacts.cid, updates.id from updates \
            join contacts on updates.contact_id = contacts.id \
            where updates.creator_id = ? \
            order by updates.id desc limit 5', (current_user,))
        updates = cur.fetchall()
        # Get next five checkins
        cur = db.execute('select name, next_checkin, id from contacts \
            where creator_id = ? \
            order by next_checkin asc limit 5', (current_user,))
        checkins = cur.fetchall()
        # Get most recent achievement
        cur = db.execute('select achievement from achievements \
            where creator_id = ? order by id desc limit 1', (current_user,))
        last_achievement = cur.fetchone()
        return render_template('main.html', current_user=current_user, \
        agenda=agenda, updates=updates, checkins=checkins, \
        quick_nav=quick_nav, new_updates=new_updates, \
        new_contacts=new_contacts)
    else:
        return render_template('welcome.html')
        current_user = None
        agenda = None
        updates = None
        checkins = None
        quick_nav = None
        new_contacts = 0
        new_updates = 0
        last_achievement = None
    return render_template('main.html', current_user=current_user, \
        agenda=agenda, updates=updates, checkins=checkins, \
        quick_nav=quick_nav, new_updates=new_updates, \
        new_contacts=new_contacts)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    current_user = session.get('current_user')
    quick_nav = QuickNavForm()
    if quick_nav.validate_on_submit():
        query = quick_nav.query.data
        db = get_db()
        query = '%' + quick_nav.query.data + '%'
        cur = db.execute('select cid, name from contacts \
            where name like ? and creator_id = ? order by name asc', \
            (query, current_user))
        results = cur.fetchall()
        if len(results) == 1:
            return redirect(url_for('view_contact', contact_id=results[0][0]))
        else:
            return render_template('search.html', results=results, \
                query=quick_nav.query.data, quick_nav=quick_nav)
    return render_template('search.html', quick_nav=quick_nav)


@app.route('/autocomplete', methods=['GET', 'POST'])
@login_required
def autocomplete():
    current_user = session.get('current_user')
    query = '%' + request.args.get('term') + '%'
    a_results = []
    db = get_db()
    cur = db.execute('select name from contacts \
        where name like ? and creator_id = ?', (query, current_user))
    for row in cur:
        a_results.append(row[0])
    return json.dumps(a_results)


@app.route('/updates')
@login_required
def view_update_stream():
    current_user = session.get('current_user')
    db = get_db()
    cur = db.execute('select updates.description, updates.created_on, \
        contacts.name, contacts.cid, updates.id from updates \
        join contacts on updates.contact_id = contacts.id \
        where updates.creator_id = ? order by updates.id desc', \
        (current_user,))
    updates = cur.fetchall()
    return render_template('updates.html', updates=updates)


@app.route('/contacts')
@login_required
def view_all_contacts():
    current_user = session.get('current_user')
    db = get_db()
    cur = db.execute('select name, last_checkin, next_checkin, cid \
        from contacts where creator_id = ? order by name asc', \
        (current_user,))
    contacts = cur.fetchall()
    return render_template('contacts.html', contacts=contacts)


@app.route('/checkins')
@login_required
def view_next_checkins(): # Should support display of most recent update as well.
    current_user = session.get('current_user')
    db = get_db()
    cur = db.execute('select cid, name, next_checkin, next_action \
        from contacts where creator_id = ? order by next_checkin asc', \
        (current_user,))
    checkins = cur.fetchall()
    return render_template('checkins.html', checkins=checkins)


@app.route('/contacts/<contact_id>', methods=['GET', 'POST'])
@login_required
def view_contact(contact_id): # Contact ID is currently derived from the primary key but it should be changed to something user-specific
    current_user=session.get('current_user')
    db = get_db()
    cur = db.execute('select name, note, last_checkin, next_checkin, \
        next_action, id from contacts where creator_id = ? and cid = ?', \
        (current_user, contact_id))
    contact = cur.fetchone()
    if not contact:
        abort(404)
    cur = db.execute('select description, created_on, id from updates \
        where creator_id = ? and contact_id = ? order by id desc', \
        (current_user, contact_id))
    updates = cur.fetchall()
    update_form = AddUpdateForm()
    if update_form.validate_on_submit():
        next_checkin = parse_checkin(update_form.checkin_text.data)
        if update_form.next_action.data == '':
            next_action = 'Touch base'
        else:
            next_action = update_form.next_action.data
        db.execute('insert into updates (description, created_on, \
            contact_id, creator_id) values (?, ?, ?, ?)', \
            (update_form.update_text.data, datetime.utcnow().date(), \
                contact[4], current_user))
        last_checkin = datetime.utcnow().date()
        db.execute('update contacts set last_checkin = ?, next_checkin = ?, \
            next_action = ? where creator_id = ? and cid = ?', \
            (last_checkin, next_checkin, next_action, current_user, \
                contact_id))
        db.commit()
        flash('Updated %s.' % (contact[0]))
        return redirect(url_for('main_view'))
    else:
        render_template('contact.html', contact=contact, updates=updates, \
            contact_id=contact_id, update_form=update_form)
    return render_template('contact.html', contact=contact, updates=updates, \
        contact_id=contact_id, update_form=update_form)


@app.route('/contacts/<contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id): # Contact ID is currently derived from the primary key but it should be changed to something user-specific
    current_user=session.get('current_user')
    db = get_db()
    cur = db.execute('select name, note, last_checkin, next_checkin, \
        next_action from contacts where creator_id = ? and cid = ?', \
        (current_user, contact_id))
    contact = cur.fetchone()
    if not contact:
        abort(404)
    form = EditContactForm()
    form.new_name.default = contact[0]
    form.new_note.default = contact[1]
    form.new_checkin.default = contact[3]
    form.new_next_action.default = contact[4]
    if form.validate_on_submit():
        new_checkin = parse_checkin(form.new_checkin.data)
        new_next_action = form.new_next_action.data
        if new_next_action == '':
            new_next_action = 'Touch base'
        db.execute('update contacts set name = ?, note = ?, \
            next_checkin = ?, next_action = ? where creator_id = ? and \
            cid = ?', (form.new_name.data, form.new_note.data, \
                new_checkin, new_next_action, \
                current_user, contact_id))
        db.commit()
        return redirect(url_for('view_contact', contact_id=contact_id))
    form.process()
    return render_template('edit_contact.html', contact=contact, form=form, \
                contact_id=contact_id)


@app.route('/contacts/<contact_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_contact(contact_id):
    current_user=session.get('current_user')
    db = get_db()
    cur = db.execute('select name, note, last_checkin, next_checkin, \
        next_action from contacts where creator_id = ? and cid = ?', \
        (current_user, contact_id))
    contact = cur.fetchone()
    if not contact:
        abort(404)
    db.execute('delete from contacts where creator_id = ? and cid = ?', \
        (current_user, contact_id))
    db.execute('delete from updates where creator_id = ? \
        and contact_id = ?', (current_user, contact_id))
    db.commit()
    flash('%s has been deleted.' % (contact[0]))
    return redirect(url_for('main_view'))


@app.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    current_user = session.get('current_user')
    form = AddContactForm()
    if form.validate_on_submit():
        current_date = datetime.utcnow().date()
        name = form.name.data
        note = form.note.data
        update = 'Contact created'
        next_action = form.next_action.data
        if next_action == '':
            next_action = 'Touch base'
        next_checkin = parse_checkin(form.checkin.data)
        db = get_db()
        # Get highest cid or start from 1
        # The cid serves as the externally visible contact id
        # and starts from 1 each user.
        cur = db.execute('select max(cid) from contacts \
            where creator_id = ?', (current_user,))
        highest_cid = cur.fetchone()
        if highest_cid[0] == None:
            cid = 1
        else:
            cid = highest_cid[0] + 1
        db.execute('insert into contacts (cid, name, note, next_checkin, \
            next_action, created_on, creator_id) \
            values (?, ?, ?, ?, ?, ?, ?)', \
            (cid, name, note, next_checkin, next_action, current_date, \
            current_user))
        db.commit()
        cur = db.execute('select id from contacts where cid = ? \
            and next_checkin = ? and creator_id = ?', \
            (cid, next_checkin, current_user))
        contact = cur.fetchone()
        contact_id = contact[0]
        db.execute('insert into updates (description, created_on, \
            contact_id, creator_id) values (?, ?, ?, ?)', \
            (update, current_date, contact_id, current_user))
        db.commit()
        flash('Added %s' % (name))
        return redirect(url_for('main_view'))
    return render_template('add_contact.html', form=form)


@app.route('/ring_the_bell', methods=['GET', 'POST'])
@login_required
def ring_the_bell():
    form = RingTheBellForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute('insert into achievements (achievement, created_on, \
            creator_id) values (?, ?, ?)', \
            (form.achievement.data, datetime.utcnow().date(), \
                session.get('current_user')))
        db.commit()
        flash('Congrats! Keep it up!')
        return redirect(request.referrer)
    return render_template('ring_the_bell.html', form=form)