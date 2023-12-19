from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, FloatField, DateField, SelectField, ValidationError, DecimalField, IntegerField
from datetime import datetime
from wtforms.validators import DataRequired , NumberRange, EqualTo, ValidationError, Regexp, AnyOf
from wtforms.widgets import NumberInput, Input
from markupsafe import Markup
import re



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def validate_numeric(form, field):
    try:
        float(field.data)
    except ValueError:
        raise ValidationError('Please enter a valid numeric value.')


class CurrencyInput(Input):
    input_type = 'text'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'text')
        field_id = kwargs.pop('id', field.id)
        html = ['<div class="input-group">']
        html.append('<span class="input-group-addon">$</span>')
        html.append(super(CurrencyInput, self).__call__(field, id=field_id, **kwargs))
        html.append('</div>')
        return Markup(''.join(html))


class PercentageInput(Input):
    input_type = 'text'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'text')
        field_id = kwargs.pop('id', field.id)
        html = ['<div class="input-group">']
        html.append(super(PercentageInput, self).__call__(field, id=field_id, **kwargs))
        html.append('<span class="input-group-addon">%</span>')
        html.append('</div>')
        return Markup(''.join(html))




        


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
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(255))
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('expenses', lazy=True))


class BudgetForm(FlaskForm):
    category_choices = [
        ('housing', 'Housing'),
        ('utilities', 'Utilities'),
        ('groceries', 'Groceries'),
        ('transportation', 'Transportation'),
        ('insurance', 'Insurance'),
        ('debt_payments', 'Debt Payments'),
        ('entertainment', 'Entertainment'),
        ('personal_care', 'Personal Care'),
        ('health_and_fitness', 'Health and Fitness'),
        ('savings', 'Savings'),
        ('clothing', 'Clothing'),
        ('gifts', 'Gifts'),
        ('travel', 'Travel'),
        ('miscellaneous', 'Miscellaneous')
    ]

    category = SelectField('Category', choices=category_choices, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0), validate_numeric], widget=CurrencyInput())
    frequency = StringField('Frequency', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])



class ExpenseForm(FlaskForm):
    category_choices = [
        ('housing', 'Housing'),
        ('utilities', 'Utilities'),
        ('groceries', 'Groceries'),
        ('transportation', 'Transportation'),
        ('insurance', 'Insurance'),
        ('debt_payments', 'Debt Payments'),
        ('entertainment', 'Entertainment'),
        ('personal_care', 'Personal Care'),
        ('health_and_fitness', 'Health and Fitness'),
        ('savings', 'Savings'),
        ('clothing', 'Clothing'),
        ('gifts', 'Gifts'),
        ('travel', 'Travel'),
        ('miscellaneous', 'Miscellaneous')
    ]

    category = SelectField('Category', choices=category_choices, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()])
    notes = StringField('Notes')


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    planned_income = db.Column(db.Float, nullable=False)
    actual_income = db.Column(db.Float)
    date = db.Column(db.Date, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('income', lazy=True))


class IncomeForm(FlaskForm):
    source_choices = [
        ('salary', 'Salary'),
        ('freelance', 'Freelance'),
        ('side_hustle', 'Side Hustle'),
        ('bonus', 'Bonus'),
        ('business_income', 'Business Income'),
        ('interest_income', 'Interest Income'),
        ('online_platforms', 'Online Platforms'),
        ('pensions', 'Pensions')
    ]

    """def validate_numeric(form, field):
        if not re.match(r'^\d+(\.\d+)?$', str(field.data)):
            raise ValidationError('Please enter a valid numeric value.')"""

    source = SelectField('Source', choices=source_choices, validators=[DataRequired()])
    planned_income = DecimalField('Planned Income', validators=[DataRequired(), NumberRange(min=0)], widget=CurrencyInput())
    actual_income = DecimalField('Actual Income', widget=CurrencyInput())
    date = DateField('Date', validators=[DataRequired()])

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debt_type = db.Column(db.String(50), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False)
    months = db.Column(db.Integer, nullable=False)  
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('debt', lazy=True))



class DebtForm(FlaskForm):
    debt_type_choices = [('student_loans', 'Student Loans'),
                         ('credit_cards', 'Credit Cards'),
                         ('mortgage', 'Mortgage'),
                         ('auto_loan', 'Auto Loan'),
                         ('personal_loan', 'Personal Loan'),
                         ('other_loan', 'Other Loan')]

    debt_type = SelectField('Debt Type', choices=debt_type_choices, validators=[DataRequired()])
    principal_amount = DecimalField('Principal Amount', validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")])
    interest_rate = DecimalField('Interest Rate', widget=NumberInput(), validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")])
    monthly_payment = DecimalField('Monthly Payment', validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")], widget=CurrencyInput())
    months = IntegerField('Months', validators=[DataRequired(), NumberRange(min=0, message="Please enter a valid numeric value.")])

    remaining_balance = DecimalField('Remaining Balance', validators=[DataRequired()])


    

class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    running_balance = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    budget = db.relationship('Budget', backref=db.backref('transaction_history', lazy=True))


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

@app.route('/budget1', methods=['GET', 'POST'])
def add_budget():
    form = BudgetForm()

    if form.validate_on_submit():
        #print(form.category)
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

        return jsonify({
            'category': category,
            'amount': amount,
            'frequency': frequency,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
    # Pass the form variable to the template
    return render_template('budget1.html', form=form)


@app.route('/expenses', methods=['POST', 'GET'])
def record_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        date = form.date.data
        notes = form.notes.data

        budget_id = request.form.get('budget_id')
        new_expense = Expense(category=category, amount=amount, date=date, notes=notes, budget_id=budget_id)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense recorded successfully!', 'success')

    return render_template('expense.html', form=form)
    


@app.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
def edit_budget(id):
    budget_item = Budget.query.get_or_404(id)
    form = BudgetForm(obj=budget_item)
    if form.validate_on_submit():
        form.populate_obj(budget_item)
        db.session.commit()
        return redirect(url_for('budget1'))
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
    return redirect(url_for('budget1'))


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

        # Pass the form and income data to the template with different variable names
        return render_template('income.html', income_form=form, income_data=income_data)

    # Pass the form to the template
    return render_template('income.html', income_form=form)


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
        remaining_balance = calculate_remaining_balance(principal_amount, interest_rate, form.months.data)

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


def calculate_remaining_balance(principal, interest_rate, months):
    r = interest_rate / 12  # Monthly interest rate
    n = months  # Total number of payments

    remaining_balance = principal * (1 - (1 + r) ** -n) / r

    return round(remaining_balance, 2)


@app.route('/transaction_history', methods=['GET', 'POST'])
def record_transaction_history():
    form = TransactionHistoryForm()

    # Fetch data only if it's not the first load (i.e., after form submission)
    transaction_history_data = TransactionHistory.query.all() if request.method == 'POST' else []

    if request.method == 'POST' and form.validate_on_submit():
        # Your form processing logic
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

        # Fetch the updated transaction history data from the database
        transaction_history_data = TransactionHistory.query.all()

        # Flash a success message (if you want)
        flash('Transaction history entry added successfully!', 'success')

    return render_template('transaction_history.html', all_transactions=form, transaction_history_data=transaction_history_data)

@app.route('/edit_transaction_history/<int:id>', methods=['GET', 'POST'])
def edit_transaction_history(id):
    transaction_item = TransactionHistory.query.get_or_404(id)
    form = TransactionHistoryForm(obj=transaction_item)

    if form.validate_on_submit():
        form.populate_obj(transaction_item)
        db.session.commit()
        # Flash a success message (if you want)
        flash('Transaction history entry updated successfully!', 'success')
        return redirect(url_for('transaction_history'))

    return render_template('edit_transaction_history.html', form=form, transaction_item=transaction_item)


@app.route('/delete_transaction_history/<int:id>', methods=['POST'])
def delete_transaction_history(id):
    transaction_item = TransactionHistory.query.get_or_404(id)
    db.session.delete(transaction_item)
    db.session.commit()
    # Flash a success message (if you want)
    flash('Transaction history entry deleted successfully!', 'success')
    return redirect(url_for('transaction_history'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)