from flask import Flask
from flask import render_template, redirect, url_for, request,jsonify
from flaskext.mysql import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from datetime import datetime

mysql = MySQL()
app = Flask(__name__, template_folder='template')
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '#9p18AA0085'
app.config['MYSQL_DATABASE_DB'] = 'inventory_management'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

wrt = 1
mutex = 1
supplier_count = 0

queue = []

class SupplierRegistrationForm(FlaskForm):
    sid = StringField('Supplier ID',
                           validators=[DataRequired(), Length(min=1, max=10)])
    fname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    street = StringField('Street', validators=[DataRequired(), Length(min=1, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=20)])
    state = StringField('State', validators=[DataRequired(), Length(min=1, max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(min=1, max=20)])
    phone = StringField('Phone', validators=[DataRequired()], render_kw={"placeholder": "If multiple, separate them by a space"})
    submit = SubmitField('Register')

class CustomerRegistrationForm(FlaskForm):
    sid = StringField('Customer ID',
                           validators=[DataRequired(), Length(min=1, max=10)])
    fname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    street = StringField('Street', validators=[DataRequired(), Length(min=1, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=20)])
    state = StringField('State', validators=[DataRequired(), Length(min=1, max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(min=1, max=20)])
    phone = StringField('Phone', validators=[DataRequired()], render_kw={"placeholder": "If multiple, separate them by a space"})
    submit = SubmitField('Register')

class ProductRegistrationForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired(), Length(min=1, max=20)])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=20)])
    cp = StringField('Cost Price', validators=[DataRequired(), Length(min=1, max=20)])
    sp = StringField('Selling Price', validators=[DataRequired(), Length(min=1, max=20)])   
    submit = SubmitField('Register')

class InventoryRegistrationForm(FlaskForm):
    iid = StringField('Inventory ID',validators=[DataRequired(), Length(min=1, max=10)])
    street = StringField('Street', validators=[DataRequired(), Length(min=1, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=1, max=20)])
    state = StringField('State', validators=[DataRequired(), Length(min=1, max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(min=1, max=20)])   
    submit = SubmitField('Register')

class SupplyForm(FlaskForm):
    sid = StringField('Supplier ID',validators=[DataRequired(), Length(min=1, max=10)])
    iid = StringField('Inventory ID',validators=[DataRequired(), Length(min=1, max=10)])
    brand = StringField('Brand', validators=[DataRequired(), Length(min=1, max=20)])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=20)])
    qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Done')

class SmallForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired(), Length(min=1, max=20)])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=20)])
    qty = IntegerField('Quantity', validators=[DataRequired()])
    

class BuyForm(FlaskForm):
    cid = StringField('Customer ID',validators=[DataRequired(), Length(min=1, max=10)])
    iid = StringField('Inventory ID',validators=[DataRequired(), Length(min=1, max=10)])
    products = FieldList(FormField(SmallForm),min_entries=1)
    add = SubmitField('Add')
    submit = SubmitField('Done')

class SearchForm(FlaskForm):
    brand = StringField('Search',validators=[DataRequired(), Length(min=1)])    
    submit = SubmitField('Search')

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        data = request.form["brand"]
        print(data)
        query = "select storedin.category,storedin.iid,storedin.iqty,product.sp from storedin, product where storedin.brand = \"%s\" and storedin.brand = product.brand and storedin.category = product.category;"%(data)
        cursor.execute(query)
        x = cursor.fetchall()
        return render_template('display.html',items=x,isBrand = False,brand=data)
    return render_template('index.html')


@app.route("/allProducts", methods = ["GET", "POST"])
def allProducts():
    query = "select storedin.category,storedin.iid,storedin.iqty,product.sp,storedin.brand from storedin, product where storedin.brand = product.brand and storedin.category = product.category;"
    cursor.execute(query)
    x = cursor.fetchall()
    return render_template('display.html',items=x,isBrand = True)
    
@app.route("/supplierRegister", methods = ["GET", "POST"])
def supplierRegister():
    form = SupplierRegistrationForm()
    if form.validate_on_submit():
        
        sup = "insert into Supplier values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\");"%(form.sid.data,form.fname.data,form.lname.data,form.street.data,form.city.data)
        cursor.execute(sup)
        phoneNos = form.phone.data.split()
        for x in phoneNos:
            cursor.execute("Insert into Phone values(\"%s\",\"%s\");"%(form.sid.data,x))
        cursor.execute("Select city from address where city = \"%s\";"%(form.city.data))
        data = cursor.fetchall()
        
        if len(data) == 0:
            cursor.execute("Insert into Address values(\"%s\",\"%s\",\"%s\");"%(form.city.data,form.state.data,form.country.data))
        else:
            print(data)
        
        conn.commit()
        return redirect(url_for('home'))
    return render_template('supplierRegister.html', form=form)

@app.route("/customerRegister", methods = ["GET","POST"])
def customerRegister():
    form = CustomerRegistrationForm()
    if form.validate_on_submit():
        sup = "insert into Customer values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\");"%(form.sid.data,form.fname.data,form.lname.data,form.street.data,form.city.data)
        cursor.execute(sup)
        phoneNos = form.phone.data.split()
        for x in phoneNos:
            cursor.execute("Insert into Phone values(\"%s\",\"%s\");"%(form.sid.data,x))
        cursor.execute("Select city from address where city = \"%s\";"%(form.city.data))
        data = cursor.fetchall()
        
        if len(data) == 0:
            cursor.execute("Insert into Address values(\"%s\",\"%s\",\"%s\");"%(form.city.data,form.state.data,form.country.data))
        else:
            print(data)
        
        conn.commit()
        return redirect(url_for('home'))
    return render_template('customerRegister.html', form=form)


@app.route("/productRegister", methods = ["GET","POST"])
def productRegister():
    form = ProductRegistrationForm()
    if form.validate_on_submit():
        sup = "insert into Product values(\"%s\",\"%s\",\"%s\",\"%s\");"%(form.brand.data,form.category.data,form.cp.data,form.sp.data)
        cursor.execute(sup)
        conn.commit()
        return redirect(url_for('home'))
    return render_template('productRegister.html', form=form)

@app.route("/inventoryRegister", methods = ["GET","POST"])
def inventoryRegister():
    form = InventoryRegistrationForm()
    if form.validate_on_submit():
        sup = "insert into Inventory values(\"%s\",\"%s\",\"%s\");"%(form.iid.data,form.street.data,form.city.data)
        cursor.execute(sup)
        cursor.execute("Select city from address where city = \"%s\";"%(form.city.data))
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute("Insert into Address values(\"%s\",\"%s\",\"%s\");"%(form.city.data,form.state.data,form.country.data))

        conn.commit()
        return redirect(url_for('home'))
    return render_template('inventoryRegister.html', form=form)


@app.route("/supply", methods = ["GET","POST"])
def supply():
    global mutex
    global supplier_count
    global wrt
    global queue
    form = SupplyForm()
    if form.validate_on_submit():

        queue.append('S')
        while mutex <= 0:
            pass
        mutex -= 1

        while queue[0]=='W':
            pass

        if supplier_count == 0:
            while wrt <= 0:
                pass
            wrt -= 1

        supplier_count += 1
        mutex += 1

        query = "Insert into supply values(\"%s\",\"%s\",\"%s\",%d);"%(form.sid.data,form.brand.data,form.category.data,form.qty.data)
        cursor.execute(query)

        cursor.execute("select * from storedin where iid = \"%s\" and brand = \"%s\" and category = \"%s\";"%(form.iid.data,form.brand.data,form.category.data))
        data = cursor.fetchall()
        if(len(data) == 0):
            query = "Insert into storedin values(\"%s\",\"%s\",\"%s\",%d);"%(form.brand.data,form.category.data,form.iid.data,form.qty.data)
        else:
            query = "Update storedin set iqty = iqty + %d where iid = \"%s\" and brand = \"%s\" and category = \"%s\";"%(form.qty.data,form.iid.data,form.brand.data,form.category.data)
        cursor.execute(query)
        conn.commit()

        while mutex <= 0:
            pass
        mutex -= 1

        supplier_count -= 1
        queue.pop(0)
        if supplier_count == 0:
            wrt += 1
        mutex += 1

        return redirect(url_for("home"))
    return render_template('supply.html', form=form)

@app.route("/buy", methods = ["GET","POST"])
def buy():
    global mutex
    global supplier_count
    global wrt
    global queue
    form = BuyForm()

    if form.add.data:
        getattr(form,'products').append_entry()
        return render_template('buy.html', form=form)
    if form.validate_on_submit():

        queue.append('W')
        
        while(wrt<=0):
            pass
        wrt -= 1

        now = datetime.now()
        prod = []
        
        for x in form.products.data:
            cursor.execute("select * from storedin where iid = \"%s\" and brand = \"%s\" and category = \"%s\";"%(form.iid.data,x['brand'],x['category']))
            check = cursor.fetchall()
            print(check)
            if(len(check)==0):
                wrt += 1
                prod.append((x['brand'],x['category'],x['qty']))
                return render_template('naya.html', prod=prod)
            if(check[0][3] < x['qty']):
                prod.append((x['brand'],x['category'],x['qty']))

        
        if(len(prod) > 0):
            wrt += 1
            queue.pop(0)
            return render_template('problem.html', prod=prod)

        q1 = "select * from cart where cid = \"%s\";"%(form.cid.data)
        cursor.execute(q1)
        no = len(cursor.fetchall())
        orderId = form.cid.data + "_" + str(no+1)
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        query = "Insert into cart values(\"%s\",\"%s\",\"%s\");"%(orderId,dt_string,form.cid.data)
        cursor.execute(query)

        for x in form.products.data:
            query = 'update storedin set iqty = iqty - %d where iid = \"%s\" and brand = \"%s\" and category = \"%s\" and iqty >= %d'%(x['qty'],form.iid.data,x['brand'],x['category'],x['qty'])
            cursor.execute(query)
            query = 'insert into consists values(\"%s\",\"%s\",\"%s\",%d);'%(orderId,x['brand'],x['category'],x['qty'])
            cursor.execute(query)

        conn.commit()
        queue.pop(0)
        wrt += 1
        return redirect(url_for("home"))
    return render_template('buy.html', form=form)


if __name__ == "__main__":
    app.debug = True
    app.run()