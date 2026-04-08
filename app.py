from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    name = db.Column(db.String(100))
    price = db.Column(db.String(20))
    img = db.Column(db.String(200))
    student_id = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    category = db.Column(db.String(30))
    description = db.Column(db.String(300))
    sold = db.Column(db.Boolean, default=False)
    time = db.Column(db.String(30))
    views = db.Column(db.Integer, default=0)
    password = db.Column(db.String(50))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    keyword = request.args.get('q', '').strip()
    if keyword:
        items = Item.query.filter(Item.name.contains(keyword)).all()
    else:
        items = Item.query.all()
    sell_count = sum(1 for i in Item.query.all() if i.type == "sell" and not i.sold)
    buy_count = sum(1 for i in Item.query.all() if i.type == "buy")
    sold_count = sum(1 for i in Item.query.all() if i.sold)
    return render_template('index.html', items=items,
                           sell_count=sell_count,
                           buy_count=buy_count,
                           sold_count=sold_count,
                           keyword=keyword)

@app.route('/view/<int:item_id>')
def add_view(item_id):
    item = Item.query.get(item_id)
    if item:
        item.views = (item.views or 0) + 1
        db.session.commit()
    return jsonify({'views': item.views})

@app.route('/add_sell', methods=['POST'])
def add_sell():
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '').strip()
    img = request.form.get('img', '').strip()
    student_id = request.form.get('student_id', '').strip()
    contact = request.form.get('contact', '').strip()
    category = request.form.get('category', '其他').strip()
    description = request.form.get('description', '').strip()
    password = request.form.get('password', '').strip()
    if not name or not price or not student_id or not password:
        return redirect('/')
    item = Item(
        type="sell", name=name, price=price, img=img,
        student_id=student_id, contact=contact,
        category=category, description=description,
        sold=False, time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        views=0, password=password
    )
    db.session.add(item)
    db.session.commit()
    return redirect('/')

@app.route('/add_buy', methods=['POST'])
def add_buy():
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '').strip()
    student_id = request.form.get('student_id', '').strip()
    contact = request.form.get('contact', '').strip()
    description = request.form.get('description', '').strip()
    password = request.form.get('password', '').strip()
    if not name or not price or not student_id or not password:
        return redirect('/')
    item = Item(
        type="buy", name=name, price=price,
        student_id=student_id, contact=contact,
        description=description,
        time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        views=0, password=password
    )
    db.session.add(item)
    db.session.commit()
    return redirect('/')

@app.route('/sold/<int:item_id>', methods=['POST'])
def sold(item_id):
    item = Item.query.get(item_id)
    password = request.form.get('password', '').strip()
    if item and item.type == "sell" and item.password == password:
        item.sold = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    item = Item.query.get(item_id)
    password = request.form.get('password', '').strip()
    if item and item.password == password:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)