from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from .. import db, babel, cfg
from ..models import *
from . import products
from .forms import ProductForm, CommentForm, FindProductForm


@products.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.date_added.desc()).paginate(
        page, per_page=current_app.config['PRODUCTS_PER_PAGE'],
        error_out=False)
    product_list = pagination.items
    return render_template('products/index.html', products=product_list, pagination=pagination)

@products.route('/find_product', methods=['GET', 'POST'])
def find_product():
    form = FindProductForm()
    if form.validate_on_submit():
        result = Product.query.filter_by(type=form.type.data).filter_by(serial=form.serial.data).first()
        if result is not None:
            flash(gettext(u'Product with serial {serial} found.'.format(serial=form.serial.data)))
            return redirect(url_for('products.product', id=result.id))

        flash(gettext(u'Product with serial {serial} not found.'.format(serial=form.serial.data)))
    return render_template('products/find_product.html', form=form)

@products.route('/product/<int:id>', methods=['GET', 'POST'])
def product(id):
    product = Product.query.get_or_404(id)
    comment = None
    form = None
    if current_user.is_authenticated():
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              product=product,
                              author=current_user
                              )
    if comment:
        db.session.add(comment)
        db.session.commit()
        if comment:
            flash(gettext(u'Your comment has been published.'))
        return redirect(url_for('.product', id=product.id) + '#top')
    comments_query = product.comments
    page = request.args.get('page', 1, type=int)
    pagination = comments_query.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    stations = {}
    headers = {}
    if current_user.is_authenticated():
        headers['X-XSS-Protection'] = '0'
    return render_template('products/product.html', product=product, form=form,
                           comments=comments, pagination=pagination),\
           200, headers


@products.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if not current_user.is_admin and product.author != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        form.to_model(product)
        db.session.add(product)
        db.session.commit()
        flash(gettext(u'The product was updated successfully.'))
        return redirect(url_for('.product', id=product.id))
    form.from_model(product)
    return render_template('products/edit_product.html', form=form)


