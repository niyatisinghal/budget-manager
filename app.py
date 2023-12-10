from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, FloatField, DateField, SelectField
from datetime import datetime
from wtforms.validators import DataRequired , NumberRange # Add this import
from wtforms.widgets import NumberInput


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
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('expenses', lazy=True))


class BudgetForm(FlaskForm):
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = StringField('Frequency', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])



class ExpenseForm(FlaskForm):
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    planned_income = db.Column(db.Float, nullable=False)
    actual_income = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False)


class IncomeForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired()])
    planned_income = FloatField('Planned Income', validators=[DataRequired()])
    actual_income = FloatField('Actual Income')
    date = DateField('Date', validators=[DataRequired()])


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debt_type = db.Column(db.String(50), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False)


class DebtForm(FlaskForm):
    debt_type = StringField('Debt Type', validators=[DataRequired()])
    principal_amount = FloatField('Principal Amount', validators=[DataRequired()])
    interest_rate = FloatField('Interest Rate', validators=[DataRequired()])
    monthly_payment = FloatField('Monthly Payment', validators=[DataRequired()])
    remaining_balance = FloatField('Remaining Balance', validators=[DataRequired()])


class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    running_balance = db.Column(db.Float, nullable=False)


class TransactionHistoryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category_choices = [('income', 'Income'), ('expense', 'Expense'), ('investment', 'Investment'), ('saving', 'Saving'), ('miscellaneous', 'Miscellaneous')]
    category = SelectField('Category', choices=category_choices, validators=[DataRequired()])    
    amount = FloatField('Amount', widget=NumberInput(), validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")])
    running_balance = FloatField('Running Balance', widget=NumberInput(), validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")])


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/budget', methods=['GET', 'POST'])
def add_budget():
    form = BudgetForm()

    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        frequency = form.frequency.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        new_budget = Budget(category=category, amount=amount, frequency=frequency, start_date=start_date, end_date=end_date)

        db.session.add(new_budget)
        db.session.commit()

        # Retrieve the updated budget data from the database
        budget_data = Budget.query.all()

        # Flash a success message
        flash('Budget item added successfully!', 'success')

        return render_template('budget.html', allbudget=form, budget_data=budget_data)
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


@app.route('/income', methods=['GET', 'POST'])
def add_income():
    form = IncomeForm()

    if form.validate_on_submit():
        source = form.source.data
        planned_income = form.planned_income.data
        actual_income = form.actual_income.data
        date = form.date.data

        new_income = Income(source=source, planned_income=planned_income, actual_income=actual_income, date=date)

        db.session.add(new_income)
        db.session.commit()

        # Retrieve the updated income data from the database
        income_data = Income.query.all()

        # Flash a success message
        flash('Income entry added successfully!', 'success')

        return render_template('income.html', allincome=form, income_data=income_data)
    return render_template('income.html', allincome=form)

@app.route('/edit_income/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    income_item = Income.query.get_or_404(id)
    form = IncomeForm(obj=income_item)

    if form.validate_on_submit():
        form.populate_obj(income_item)
        db.session.commit()
        flash('Income entry updated successfully!', 'success')
        return redirect(url_for('view_income'))

    return render_template('editincome.html', form=form, income_item=income_item)

@app.route('/delete_income/<int:id>', methods=['POST'])
def delete_income(id):
    income_item = Income.query.get_or_404(id)
    db.session.delete(income_item)
    db.session.commit()
    flash('Income entry deleted successfully!', 'success')
    return redirect(url_for('view_income'))

@app.route('/debt', methods=['GET', 'POST'])
def add_debt():
    form = DebtForm()

    if form.validate_on_submit():
        debt_type = form.debt_type.data
        principal_amount = form.principal_amount.data
        interest_rate = form.interest_rate.data
        monthly_payment = form.monthly_payment.data
        remaining_balance = form.remaining_balance.data

        new_debt = Debt(debt_type=debt_type, principal_amount=principal_amount,
                        interest_rate=interest_rate, monthly_payment=monthly_payment,
                        remaining_balance=remaining_balance)

        db.session.add(new_debt)
        db.session.commit()

        # Retrieve the updated debt data from the database
        debt_data = Debt.query.all()

        # Flash a success message
        flash('Debt entry added successfully!', 'success')

        return render_template('debt.html', alldebt=form, debt_data=debt_data)
    return render_template('debt.html', alldebt=form)


@app.route('/transaction_history', methods=['GET', 'POST'])
def add_transaction_history():
    form = TransactionHistoryForm()

    if form.validate_on_submit():
        date = form.date.data
        description = form.description.data
        category = form.category.data
        amount = form.amount.data
        running_balance = form.running_balance.data

        new_transaction = TransactionHistory(date=date, description=description,
                                             category=category, amount=amount,
                                             running_balance=running_balance)

        db.session.add(new_transaction)
        db.session.commit()

        # Retrieve the updated transaction history data from the database
        transaction_history_data = TransactionHistory.query.all()

        # Flash a success message
        flash('Transaction history entry added successfully!', 'success')

        return render_template('transaction_history.html', all_transactions=form, transaction_history_data=transaction_history_data)
    return render_template('transaction_history.html', all_transactions=form)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)