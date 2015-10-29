from flask.ext.wtf import Form
from wtforms import SubmitField, IntegerField, SelectField, StringField
from wtforms.fields.html5 import DateTimeField, DateField
from wtforms.validators import Required, NumberRange, InputRequired, Length
from flask.ext.pagedown.fields import PageDownField
from flask.ext.babel import gettext, lazy_gettext
from wtforms.fields.simple import TextField


class ProductForm(Form):
    type = StringField(lazy_gettext('Product Type'), validators=[Required(), Length(1, 10)])
    serial = StringField(lazy_gettext('Serial Number'), validators=[Required(), Length(1, 20)])
    program_id = SelectField(lazy_gettext('Program'))
    date = StringField(lazy_gettext('Date Added'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Submit'))

    def from_model(self, product):
        self.type.data = product.type
        self.serial.data = product.serial
        self.program_id.data = unicode(product.program_id)
        self.date.data = product.date_added

    def to_model(self, product):
        product.type = self.type.data
        product.serial = self.serial.data
        product.program_id = unicode(self.program_id.data)
        product.date_added = self.date.data

    def __init__(self, program_choices):
        Form.__init__(self)
        self.program_id.choices = program_choices


class CommentForm(Form):
    body = PageDownField(lazy_gettext('Comment'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Submit'))


class FindProductForm(Form):
    type = SelectField(lazy_gettext('Product Type'), validators=[Required()])
    serial = StringField(lazy_gettext('Serial Number'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Find'))

    def __init__(self, type_choices):
        Form.__init__(self)
        self.type.choices = type_choices


class FindProductsRangeForm(Form):
    start = TextField(lazy_gettext('From'))
    end = TextField(lazy_gettext('To'))
    submit = SubmitField(lazy_gettext('Find'))
