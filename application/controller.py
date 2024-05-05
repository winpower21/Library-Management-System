from .models import *
from flask import render_template, redirect, request, url_for
from flask import current_app as app
from flask import send_file
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .functions import *
import datetime
import os


''' #### ------------------ LANDING PAGE ------------------ #### '''

@app.route('/',methods = ['GET'])
def loginpage():
    return render_template('login.html')

''' ***** #### ------------------ ADMIN METHODS ------------------ #### ***** '''

# ADMIN LOGIN

@app.route('/admin_login', methods = ['GET','POST']) 
def admin_login():
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        username = request.form.get('a_email')
        password = request.form.get('a_pass')
        admin_details = User.query.filter_by(username=username).first()
        if admin_details:
            if admin_details.type == 'admin':
                if admin_details.password == password:
                    return redirect(f'/admin/{admin_details.id}')
                else:
                    return render_template('loginerror.html', error = 'Incorrect Password')
            else:
                return render_template('loginerror.html', error = 'User is not admin. Try logging in as user.')
        else:
            return render_template('loginerror.html', error = 'User Does Not Exist. Register as new user.')


# ADMIN DASH

@app.route('/admin/<int:admin_id>', methods=['GET','POST'])
def admin_dash(admin_id):
    a_user = User.query.get(admin_id)
    top_rated_books_query = db.session.query(db.func.avg(Reviews.rating))\
                .group_by(Reviews.book_id)\
                .join(Books, Reviews.book_id==Books.id)\
                .add_columns(Books.name).all()
    
    tb_rated_labels = [row[1] for row in top_rated_books_query]
    del tb_rated_labels[5::]
    tb_rated_values = [int(row[0]) for row in top_rated_books_query]
    del tb_rated_values[5::]
    
    top_requested_books_query = db.session.query(db.func.count(Requests.id))\
                            .group_by(Requests.book_id)\
                            .join(Books, Requests.book_id==Books.id)\
                            .filter(Requests.status!="Rejected",Requests.to_date<date.today()+timedelta(365))\
                            .add_columns(Books.name).all()
    
    tb_requested_labels = [row[1] for row in top_requested_books_query]
    del tb_requested_labels[5::]
    tb_requested_values = [row[0] for row in top_requested_books_query]
    del tb_requested_values[5::]
    
    return render_template('admin_dash.html', user = a_user, \
                            tb_rated_values=tb_rated_values, \
                                tb_rated_labels=tb_rated_labels, \
                                    tb_requested_labels=tb_requested_labels, \
                                        tb_requested_values=tb_requested_values)


'''
***** #### ------------------ MANAGEMENT METHODS ------------------ #### *****
'''

'''
***** ------------------ BOOK MANAGEMENT ------------------ *****
'''

@app.route('/admin/<int:admin_id>/book_management', methods = ['GET', 'POST'])
def book_management(admin_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        if a_user.type == 'admin':
            book_list = Books.query.all()
            section_list = Sections.query.all()
            return render_template('book_management.html', user = a_user, books = book_list, sections = section_list)
        else:
            return render_template('error.html', error = 'Access Denied. You are not an admin.', user=a_user)
        
        
# ------------------ BOOK CATALOGUE ------------------


@app.route("/admin/<int:user_id>/all_books", methods = ['GET','POST'])
def allbooks(user_id):
    if request.method == 'GET':
        user_data = User.query.get(user_id)
        book_data = Books.query.all()
        return render_template('all_books.html', user = user_data, books = book_data)


# ------------------ MODIFY BOOK ------------------

@app.route('/admin/<int:admin_id>/book_management/<int:book_id>/modifybook', methods = ['GET','POST'])
def modify_book(admin_id,book_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        m_book = Books.query.filter_by(id=book_id).first()
        section_list = Sections.query.all()
        return render_template('bookmodification.html',user=a_user,book=m_book, sections = section_list )
    if request.method == 'POST':
        m_book = Books.query.filter_by(id=book_id).first()
        content = request.files['book']
        cover = request.files['cover']
        name = request.form.get('name')
        author = request.form.get('author')
        section = request.form.get('section')
        description = request.form.get('description')
        price = request.form.get('price')
        m_book.name = name
        m_book.author = author
        m_book.section = section
        m_book.description = description
        m_book.price = price
        if not content and not cover:
            db.session.commit()
        elif content and not cover:
            content.save(app.config['UPLOAD_FOLDER'],secure_filename(content))
            m_book.location = secure_filename(content.filename)
            db.session.commit()
        elif cover and not content:
            m_book.cover = secure_filename(cover.filename)
            db.session.commit()
        else:
            m_book.location = secure_filename(content.filename)
            m_book.cover = secure_filename(cover.filename)
            db.session.commit
        return redirect(url_for('book_management', admin_id = admin_id))


# ------------------ CREATE NEW BOOK ------------------

@app.route('/admin/<int:admin_id>/book_management/newbook', methods = ['GET','POST'])
def new_book(admin_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        return render_template('newbook.html', user=a_user)
    elif request.method == 'POST':
        content = request.files['book']
        cover = request.files['cover']
        name = request.form.get('name')
        author = request.form.get('author')
        section = request.form.get('section')
        description = request.form.get('description')
        price = request.form.get('price')
        book = Books(cover = secure_filename(cover.filename), name = name, author = author, section = section, description = description, price = price, location = secure_filename(content.filename))
        content.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(content.filename)))
        cover.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(cover.filename)))
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('book_management', admin_id = admin_id))
    

# ------------------ DELETE A BOOK ------------------

@app.route('/admin/<int:admin_id>/book_management/<int:book_id>/delete', methods = ['GET','POST'])
def delete_book(admin_id,book_id):
    if request.method == 'GET':
        c_book = Books.query.filter_by(id=book_id).first()
        a_user = User.query.get(admin_id)
        return render_template('deletebook.html',user=a_user,book=c_book)
    if request.method == 'POST':
        c_book = Books.query.filter_by(id=book_id).first()
        if c_book:
            db.session.delete(c_book)
            db.session.commit()
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"],c_book.location))
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"],c_book.cover))
            return redirect(url_for('book_management',admin_id=admin_id))
        else:
            return redirect(url_for('admin_error',admin_id = admin_id, message = "Book does not exist."))


''' 
***** ------------------ SECTION MANAGEMENT ------------------ *****
'''


@app.route('/admin/<int:admin_id>/section_management', methods = ['GET', 'POST'])
def section_management(admin_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        if a_user.type == 'admin':
            section_list = Sections.query.all()
            return render_template('section_management.html', user = a_user, sections = section_list)
        else:
            return render_template('error.html', error = 'Access Denied. You are not an admin.', user=a_user)


# ------------------ CREATE NEW SECTION ------------------
 
@app.route("/admin/<int:admin_id>/newsection", methods = ['GET','POST'])
def section_create(admin_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        return render_template('newsection.html', user = a_user)
    elif request.method == 'POST':
        a_user = User.query.get(admin_id)
        if a_user.type == 'admin':
            section_name = request.form.get('name')
            section_description = request.form.get('description')
            check_section = Sections.query.filter_by(name=section_name).first()
            if not check_section:
                new_section = Sections(name = section_name, description = section_description)
                db.session.add(new_section)
                db.session.commit()
                return redirect(f'/admin/{admin_id}/section_management')
            else:
                return render_template('error.html',error = "Section already exists.", user=a_user)
        else:
            return render_template('error.html', error = "Action not allowed", user=a_user)


# ------------------ UPDATE SECTION ------------------

@app.route("/admin/<int:admin_id>/section_management/<int:section_id>/modify", methods = ['GET','POST'])
def update_section(admin_id, section_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        m_section = Sections.query.filter_by(id=section_id).first()
        return render_template('section_modification.html', user = a_user, section = m_section)
    elif request.method == 'POST':
        s_name = request.form.get('name')
        s_description = request.form.get('description')
        section = Sections.query.filter_by(id=section_id).first()
        section.name = s_name
        section.description = s_description
        db.session.commit()
        return redirect(f'/admin/{admin_id}/section_management')


# ------------------ DELETE SECTION ------------------

@app.route('/admin/<int:admin_id>/section_management/<int:section_id>/delete', methods=['GET','POST'])
def delete_section(admin_id,section_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        m_section = Sections.query.filter_by(id=section_id).first()
        return render_template('deletesection.html', user=a_user, section = m_section)
    if request.method == 'POST':
            section = Sections.query.get(section_id)
            if section:
                books = Books.query.filter_by(section=section.name).all()
                if books:
                    return redirect(url_for('admin_error',admin_id = admin_id, message = 'Please remove books or change their sections having current section, before attempting delete'))
                db.session.delete(section)
                db.session.commit()
            return redirect(f'/admin/{admin_id}/section_management')



''' 
***** ------------------ REQUEST HANDLING ------------------ *****
'''


# ------------------ REQUEST MANAGEMENT LANDING PAGE ------------------

@app.route('/admin/<int:admin_id>/request_management', methods=['GET','POST'])
def request_management(admin_id):
    if request.method == 'GET':
        a_user = User.query.get(admin_id)
        requests = Requests.query\
                        .join(Books, Requests.book_id==Books.id)\
                        .join(User, User.id == Requests.user_id)\
                        .add_columns(Requests.id,Books.name,User.username,Books.author,Requests.from_date,Requests.to_date,Requests.status).all()
        all_purchases = Purchases.query\
                        .join(Books, Purchases.book_id == Books.id)\
                            .join(User, User.id == Purchases.user_id)\
                                .add_columns(Purchases.id,Books.name,User.username,Books.author,Books.section,Purchases.purchase_date).all()
        return render_template('request_management.html', user=a_user, requests= requests, purchases=all_purchases)


# ------------------ ALL REQUESTS/PURCHASES ------------------

@app.route('/admin/<int:admin_id>/<string:action>', methods=['GET'])
def all_management(admin_id, action):
    a_user = User.query.get(admin_id)
    if action == 'request':
        all_requests = Requests.query\
                        .join(Books, Requests.book_id==Books.id)\
                        .join(User, User.id == Requests.user_id)\
                        .add_columns(Requests.id,Books.name,User.username,Books.author,Requests.from_date,Requests.to_date,Requests.status).all()
        return render_template('requests.html', user=a_user, requests= all_requests)
    elif action == 'purchases':
        all_purchases = Purchases.query\
                        .join(Books, Purchases.book_id == Books.id)\
                            .join(User, User.id == Purchases.user_id)\
                                .add_columns(Purchases.id,Books.name,User.username,Books.author,Books.section,Purchases.purchase_date).all()
        return render_template('purchases.html', user=a_user, purchases = all_purchases)



# REQUEST ACTION ENDPOINT

@app.route('/admin/<int:admin_id>/<int:request_id>/<string:action>', methods=['POST'])
def request_action(admin_id,request_id,action):
    if request.method == 'POST':
        req = Requests.query.get(request_id)
        if action == 'approved':
            req.status = "Approved"
            db.session.commit()
            return redirect(url_for('request_management', admin_id=admin_id))
        elif action == 'rejected':
            req.status = "Rejected"
            db.session.commit()
            return redirect(url_for('request_management', admin_id=admin_id))




'''
***** #### ------------------ USER METHODS ------------------ #### *****
'''


# ------------------ USER REGISTRATION ------------------

@app.route('/register',methods = ['GET','POST'])
def registration():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form.get('u_email')
        pwd = request.form.get('u_pass')
        c_pwd = request.form.get('confirm-password')
        if pwd == c_pwd:
            new_user = User(username = email,password = pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('loginerror.html', error = 'Passwords do not match, check again.')

        
# ------------------ USER LOGIN ------------------

@app.route('/user_login', methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        username = request.form.get('u_email')
        password = request.form.get('u_pass')
        curr_user = User.query.filter_by(username = username).first()
        if curr_user:
            if curr_user.password == password:
                if curr_user.type == "user":
                    today = datetime.date.today()
                    print(today)
                    expired_requests = Requests.query.filter(Requests.user_id==curr_user.id,Requests.to_date<today).all()
                    print(expired_requests)
                    if expired_requests:
                        for i in expired_requests:
                            i.status = "Returned"
                            db.session.commit()
                    return redirect(f'/user/{curr_user.id}')
                else:
                    return render_template('loginerror.html', error = 'No user with given detials. If you are an admin login using admin login form.')
            else:
                return render_template('loginerror.html', error = 'Incorrect password.')
        else:
            return render_template('loginerror.html', error = 'User does not exist.')


# ------------------ USER DASH ------------------
        
@app.route('/user/<int:user_id>', methods = ['GET','POST'])
def user_dash(user_id):
    user_details = User.query.get(user_id)
    request_data = Requests.query.filter_by(user_id = user_id)\
                .join(Books, Requests.book_id == Books.id)\
                .add_columns(Requests.id,Books.id.label("book_id"),Books.name,Books.author,Requests.from_date,Requests.to_date,Requests.status).all()
                
    top_books = db.session.query(db.func.avg(Reviews.rating)).group_by(Reviews.book_id).join(Books, Reviews.book_id==Books.id).add_columns(Books.id,Books.name, Books.author,Books.section, Books.cover).all()

    user_purchases = Purchases.query.filter(Purchases.user_id==user_id)\
                    .join(Books)\
                        .add_columns(Books.id,Books.name,Books.author,Books.cover,Books.section,Books.description).limit(3).all()
    
    user_current_requests = Requests.query.filter(Requests.user_id == user_id, Requests.status!="Returned",Requests.status!="Rejected")\
                    .join(Books, Requests.book_id == Books.id)\
                    .add_columns(Requests.id,Books.id.label("book_id"),Books.name,Books.author,Requests.from_date,Requests.to_date,Requests.status).all()
    
    books = Books.query.all()
    return render_template('user_dash.html', user = user_details,  current_requests=user_current_requests, all_requests = request_data, purchases=user_purchases, books = books, popular_books = top_books) #'''requests = user_requests'''

# ------------------ BOOK CATALOGUE ------------------


@app.route("/user/<int:user_id>/bookcatalogue", methods = ['GET','POST'])
def bookcatalogue(user_id):
    if request.method == 'GET':
        user_data = User.query.get(user_id)
        book_data = Books.query.all()
        return render_template('bookcatalogue.html', user = user_data, books = book_data)
    
    
# ------------------ ALL PURCHASES PAGE ------------------    


@app.route('/user/<int:user_id>/all_purchases')
def all_user_purchases(user_id):
    c_user = User.query.get(user_id)
    user_purchases = Purchases.query.filter(Purchases.user_id==user_id)\
                    .join(Books)\
                        .add_columns(Books.id,Books.name,Books.author,Books.cover,Books.section,Books.description).all()
    return render_template('user_purchases.html', user=c_user, purchases = user_purchases)
    
# ------------------ ALL REQUESTS PAGE ------------------    


@app.route('/user/<int:user_id>/all_requests')
def all_user_requests(user_id):
    c_user = User.query.get(user_id)
    request_data = Requests.query.filter_by(user_id = user_id)\
                    .join(Books, Requests.book_id == Books.id)\
                    .add_columns(Requests.id,Books.id.label("book_id"),Books.name,Books.author,Requests.from_date,Requests.to_date,Requests.status).all()
    return render_template('user_requests.html', user=c_user, requests = request_data)

# ------------------ SECTION VIEW PAGE ------------------

@app.route('/user/<int:user_id>/sections')
def section_view(user_id):
    c_user = User.query.get(user_id)
    sections = Sections.query.all()
    return render_template('sectionview.html',user=c_user,sections = sections)

@app.route('/user/<int:user_id>/<int:section_id>/viewbooks', methods=['GET'])
def section_book_view(user_id, section_id):
    c_user = User.query.get(user_id)
    section  = Sections.query.filter(Sections.id==section_id).first()
    books = Books.query.filter(Books.section==section.name).all()
    return render_template('sectionbooks.html',user=c_user,books = books)


# ------------------ BOOK VIEW MORE PAGE ------------------

@app.route("/user/<int:user_id>/<int:book_id>", methods = ['GET','POST'])
def book_details(user_id, book_id):
    if request.method == 'GET':
        c_user = User.query.get(user_id)
        c_book = Books.query.filter_by(id = book_id).first()
        c_reviews = Reviews.query.filter_by(book_id=book_id).all()
        if c_book:
            return render_template('bookdetails.html', message=request.args.get('message'), user=c_user, book=c_book, reviews=c_reviews)


# ------------------ BOOK REQUEST AND PURCHASE------------------

@app.route("/user/<int:user_id>/<int:book_id>/<string:action>", methods = ['POST'])
def book_request(user_id,book_id,action):
    if request.method == 'POST':
        if action == 'request':
            existing_request = Requests.query.filter(Requests.user_id==user_id,Requests.book_id==book_id,Requests.status!="Returned",Requests.status!="Rejected").all()
            if not existing_request:
                user_requests_count = Requests.query.filter((Requests.user_id==user_id)&(Requests.status=="Approved")|(Requests.status=="To be Updated")).all()
                if len(user_requests_count) < 5:
                    date = request.form.get('date')
                    if date:
                        year,month,date=date_setter(date)
                        to_date = datetime.date(year,month,date)
                        new_request = Requests(user_id=user_id,book_id=book_id,to_date=to_date)
                    if not date:
                        new_request = Requests(user_id=user_id,book_id=book_id)
                    db.session.add(new_request)
                    db.session.commit()
                    return redirect(url_for('book_details', message="Request Successfully Placed", user_id = user_id, book_id=book_id))
                else:
                    return redirect(url_for('user_error',message = "Max request limit reached. Return some books to borrow more.",user_id=user_id ))
            else:
                return redirect(url_for('user_error', user_id=user_id, message = "You already have a standing request for this book. Cannot place multiple requests."))
        elif action == 'purchase':
            existing_purchase = Purchases.query.filter(Purchases.user_id==user_id,Purchases.book_id==book_id).first()
            if not existing_purchase:
                new_purchase = Purchases(user_id=user_id,book_id=book_id)
                db.session.add(new_purchase)
                db.session.commit()
                return redirect(url_for('book_details', message="Purchase Successful", user_id = user_id, book_id=book_id))
            else:
                return redirect(url_for('user_error', user_id=user_id, message = "You have purchased this book before. Cannot place multiple orders."))
    


# ------------------ BOOK DOWNLOAD AND READING ------------------

@app.route('/user/<int:user_id>/<int:book_id>/<string:action>',methods=['GET'])
def show_static_pdf(user_id,book_id,action):
    if action == 'download':
        check_purchase = Purchases.query.filter(Purchases.user_id==user_id,Purchases.book_id==book_id).first()
        if check_purchase:
            book = Books.query.get(book_id)
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'],book.location), as_attachment=True)
        else:
            return redirect(url_for('user_error', user_id = user_id, message = 'Download not allowed. Purchase book first.'))                
    elif action == 'read':
        check_requests = Requests().query.filter(Requests.user_id==user_id,Requests.book_id==book_id).first()
        if check_requests:
            book = Books.query.get(book_id)
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'],book.location), as_attachment=False)
        else:
            return redirect(url_for('user_error', user_id = user_id, message = 'Action not allowed. Request access for book first.'))  


# ------------------ BOOK RETURN ------------------

@app.route("/user/<int:user_id>/return", methods=['GET','POST'])
def book_return(user_id):
    if request.method == 'POST':
        request_id = request.form.get("request_id")
        req = Requests.query.get(request_id)
        if req:
            req.status = 'Returned'
            db.session.commit()
        return redirect(f'/user/{user_id}')
    

# ------------------ REVIEW SUBMISSION ------------------

@app.route('/user/<int:user_id>/<int:book_id>/review', methods=['GET','POST'])
def reveiw(user_id, book_id):
    if request.method == 'POST':
        check = Reviews.query.filter(Reviews.user_id==user_id,Reviews.book_id==book_id).all()
        if not check:
            review = request.form.get('review')
            rating = request.form.get('rating')
            new_review = Reviews(user_id=user_id,book_id=book_id,review=review,rating=int(rating))
            db.session.add(new_review)
            db.session.commit()
            return redirect(url_for('book_details',user_id=user_id,book_id=book_id))
        else:
            return redirect(url_for('user_error', user_id = user_id,  message = 'Multiple reviews not allowed.'))
    

# -------------------- USER PROFILE --------------------

@app.route('/user/profile/<int:user_id>/<string:action>', methods=['GET','POST'])
def view_profile(user_id, action):
    if request.method == 'GET':
        if action == 'profile':
            user = User.query.get(user_id)
            return render_template('viewuserprofile.html',user=user)
        elif action == 'edit':
            user = User.query.get(user_id)
            return render_template('edituserprofile.html',user=user)
    elif request.method == 'POST':
        if action == 'edit':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            c_password = request.form.get('confirm-password')
            user = User.query.get(user_id)
            user.name = name
            user.username = email
            db.session.commit()
            if c_password != "":
                if password == c_password:
                    user.password = password
                    db.session.commit()
                else:
                    return redirect(url_for('user_error', user_id=user_id, message = 'Passwords do not match. Try again.'))
            return redirect(url_for('view_profile', user_id=user_id, action='profile'))


''' ------------------ ERROR PAGE ------------------ '''

@app.route('/user/<int:user_id>/error', methods=['GET'])
def user_error(user_id):
    c_user = User.query.get(user_id)
    return render_template('usererror.html', error=request.args.get('message'), user=c_user)

@app.route('/admin/<int:admin_id>/error', methods=['GET'])
def admin_error(admin_id):
    c_user = User.query.get(admin_id)
    return render_template('adminerror.html', error=request.args.get('message'), user=c_user)


''' ------------------ SEARCH ------------------ '''
@app.route('/<string:type>/<int:user_id>/search', methods=['GET','POST'])
def search(user_id,type):
    print(type)
    print(user_id)
    c_user=User.query.get(user_id)
    search = request.form.get('search')
    results = Books().query.\
                whooshee_search(search).\
                order_by(Books.id.desc()).\
                all()
    if len(search) >= 3:
        if type == 'user':
            return render_template('search_results.html',results = results, user=c_user)
        elif type == 'admin':
            return render_template('admin_search_results.html',results = results, user=c_user)
    else:
        if type == 'user':
            return redirect(url_for('user_error', user_id=user_id, message = 'Search string must have at least 3 characters.'))
        elif type == 'admin':
            return redirect(url_for('admin_error',admin_id = admin_id, message = 'Search string must have at least 3 characters.'))
