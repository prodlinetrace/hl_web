from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from flask.ext.paginate import Pagination
from .. import db, babel, cfg
from ..models import *
from . import products
from .forms import ProductForm, CommentForm, FindProductForm, FindProductsRangeForm

@products.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    per_page = current_app.config['PRODUCTS_PER_PAGE']
    query = Product.query
    if start_date:
        query = query.filter(start_date <= Product.date_added)
    if end_date:
        query = query.filter(end_date >= Product.date_added)
    total = query.count()
    products = query.order_by(Product.date_added.desc()).paginate(page, per_page, False).items
    pagination = Pagination(page=page, total=total, record_name='products', per_page=per_page)
    return render_template('products/index.html', products=products, pagination=pagination)

@products.route('/find_product', methods=['GET', 'POST'])
def find_product():
    type_query = db.session.query(Product.type.distinct().label("type"))
    type_choices = [(unicode(row.type), unicode(row.type)) for row in type_query.all()]
    type_choices.insert(0, ("", "Select Product Type"))
    basic_search_form = FindProductForm(type_choices)
    date_range_search_form = FindProductsRangeForm() 

    if basic_search_form.validate_on_submit():
        result = Product.query.filter_by(type=basic_search_form.type.data).filter_by(serial=basic_search_form.serial.data).first()
        if result is not None:
            flash(gettext(u'Product with serial {serial} found.'.format(serial=basic_search_form.serial.data)))
            return redirect(url_for('products.product', id=result.id))
        
    if date_range_search_form.validate_on_submit():
        start_date = date_range_search_form.start.data
        end_date = date_range_search_form.end.data
        query = Product.query
        if start_date:
            query = query.filter(start_date <= Product.date_added)
        if end_date:
            query = query.filter(end_date >= Product.date_added)
        total = query.count()
        result = query.all()
        if result is not None:
            flash(gettext(u'{number} products found with date range: {start} to {end}.'.format(number=len(result), start=start_date, end=end_date)))
            return redirect(url_for('products.index', start_date=start_date, end_date=end_date))


        flash(gettext(u'Product with serial {serial} not found.'.format(serial=form.serial.data)))
    return render_template('products/find_product.html', basic_search_form=basic_search_form, date_range_search_form=date_range_search_form)

@products.route('/product/<id>', methods=['GET', 'POST'])
def product(id):
    product = Product.query.get_or_404(id)
    comment = None
    form = None
    if current_user.is_authenticated():
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data, product=product, author=current_user)
    if comment:
        db.session.add(comment)
        db.session.commit()
        flash(gettext(u'Your comment has been published.'))
        return redirect(url_for('.product', id=product.id) + '#top')

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMMENTS_PER_PAGE']
    total = product.comments.count()
    comments = product.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page, False).items
    pagination = Pagination(page=page, total=total, record_name='comments', per_page=per_page)
    stations = {}
    headers = {}
    if current_user.is_authenticated():
        headers['X-XSS-Protection'] = '0'
    return render_template('products/product.html', product=product, form=form, comments=comments, pagination=pagination), 200, headers

@products.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if not current_user.is_admin and product.author != current_user:
        abort(403)
    program_choices = [(unicode(program.id), unicode("[{id}] - {name}".format(id=program.id, name=program.name))) for program in Program.query.order_by(Program.id.asc())]
    form = ProductForm(program_choices)
    if form.validate_on_submit():
        form.to_model(product)
        db.session.add(product)
        db.session.commit()
        flash(gettext(u'The product was updated successfully.'))
        return redirect(url_for('.product', id=product.id))
    form.from_model(product)
    return render_template('products/edit_product.html', form=form)
