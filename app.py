from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, FloatField


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('expenses', lazy=True))


class BudgetForm(FlaskForm):
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)


class ExpenseForm(FlaskForm):
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/budget', methods=['GET', 'POST'])
def add_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        new_budget = Budget(category=category, amount=amount)
        db.session.add(new_budget)
        db.session.commit()
        return redirect(url_for('budget'))
    return render_template('budget.html', allbudget=form)


@app.route('/expenses', methods=['POST', 'GET'])
def record_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        budget_id = request.form.get('budget_id')
        new_expense = Expense(category=category, amount=amount)
        db.session.add(new_expense)
        db.session.commit()
    return render_template('expense.html', form=form)
    


@app.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
def edit_budget(id):
    budget_item = Budget.query.get_or_404(id)
    form = BudgetForm(obj=budget_item)
    if form.validate_on_submit():
        form.populate_obj(budget_item)
        db.session.commit()
        return redirect(url_for('budget'))
    return render_template('editbudget.html', form=form, budget_item=budget_item)

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense_item = Expense.query.get_or_404(id)

    if request.method == 'POST':
        category = request.form.get('category')
        amount_str = request.form.get('amount')

        print(f"Category: {category}, Amount String: {amount_str}")

        if amount_str is not None:
            try:
                amount = float(amount_str)
                expense_item.category = category
                expense_item.amount = amount
                db.session.commit()
                return redirect(url_for('expenses'))
            except ValueError as e:
                print(f"Error converting amount to float: {e}")

    return render_template('editexpense.html', expense_item=expense_item)


@app.route('/delete_budget/<int:id>', methods=['POST'])
def delete_budget(id):
    budget_item = Budget.query.get_or_404(id)
    db.session.delete(budget_item)
    db.session.commit()
    return redirect(url_for('budget'))


@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    expense_item = Expense.query.get_or_404(id)
    db.session.delete(expense_item)
    db.session.commit()
    return redirect(url_for('expenses'))


if __name__ == '__main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)