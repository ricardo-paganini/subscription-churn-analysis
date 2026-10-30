import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

total_customers = 3000
start_date = pd.Timestamp('2025-01-01')
end_date = pd.Timestamp('2025-12-31')


###### Criando a base ######

states = ['PR', 'SP', 'SC', 'RS', 'MG', 'RJ']
state_weights = [30, 25, 15, 12, 10, 8]

plan_fees = {'Básico 100MB': 79.90, 'Intermediário 300MB': 109.90, 'Premium 600MB': 149.90}
plans = list(plan_fees.keys())
plan_weights = [45, 35, 20]

contracts = ['Mensal', 'Anual', 'Bienal']
contract_weights = [50, 30, 20]

payment_methods = ['Boleto', 'Cartão de crédito', 'Pix', 'Débito automático']
payment_weights = [30, 25, 20, 25]

customers = pd.DataFrame({
    'customer_id': range(1, total_customers + 1),
    'state': random.choices(states, weights=state_weights, k=total_customers),
    'signup_date': pd.to_datetime('2019-06-01') + pd.to_timedelta(np.random.randint(0, 2314, total_customers), unit='D'),
    'plan': random.choices(plans, weights=plan_weights, k=total_customers),
    'contract_type': random.choices(contracts, weights=contract_weights, k=total_customers),
    'payment_method': random.choices(payment_methods, weights=payment_weights, k=total_customers)
})

customers['monthly_fee'] = customers['plan'].map(plan_fees)

# churn risk: monthly contracts, new customers and boleto payers cancel more
contract_risk = {'Mensal': 0.25, 'Anual': 0.08, 'Bienal': 0.03}
churn_prob = customers['contract_type'].map(contract_risk)

tenure_months = (start_date - customers['signup_date']).dt.days / 30
churn_prob = churn_prob + np.where(tenure_months < 12, 0.12, 0)
churn_prob = churn_prob + np.where(customers['payment_method'] == 'Boleto', 0.05, 0)
churn_prob = churn_prob + np.where(customers['plan'] == 'Básico 100MB', 0.06, 0)

churned = np.random.rand(total_customers) < churn_prob

# cancel date: a random day inside the observation window, after the signup
first_day = customers['signup_date'].clip(lower=start_date)
days_left = (end_date - first_day).dt.days
cancel_offset = (np.random.rand(total_customers) * days_left).astype(int)
customers['cancel_date'] = (first_day + pd.to_timedelta(cancel_offset, unit='D')).where(churned)

customers.to_csv('customers.csv', index=False)
print('customers.csv created:', customers.shape)


###### Gerando os chamados de suporte ######

last_day = customers['cancel_date'].fillna(end_date)

active_window = pd.DataFrame({
    'customer_id': customers['customer_id'],
    'first_day': first_day,
    'active_days': (last_day - first_day).dt.days
})

ticket_reasons = ['Lentidão', 'Queda de conexão', 'Cobrança', 'Instalação', 'Dúvidas']
ticket_weights = [25, 25, 20, 10, 20]

# customers who cancel open more tickets
tickets_per_customer = np.random.poisson(np.where(churned, 1.9, 1.0))

tickets = pd.DataFrame({'customer_id': np.repeat(customers['customer_id'], tickets_per_customer)})
tickets = tickets.merge(active_window, on='customer_id')

ticket_offset = (np.random.rand(len(tickets)) * tickets['active_days']).astype(int)
tickets['open_date'] = tickets['first_day'] + pd.to_timedelta(ticket_offset, unit='D')
tickets['reason'] = random.choices(ticket_reasons, weights=ticket_weights, k=len(tickets))

tickets = tickets[['customer_id', 'open_date', 'reason']].sort_values('open_date').reset_index(drop=True)
tickets.insert(0, 'ticket_id', range(1, len(tickets) + 1))

tickets.to_csv('tickets.csv', index=False)
print('tickets.csv created:', tickets.shape)


###### Gerando os pagamentos ######

due_dates = pd.DataFrame({'due_date': pd.to_datetime([f'2025-{month:02d}-10' for month in range(1, 13)])})

billing_base = customers[['customer_id', 'monthly_fee', 'payment_method']].assign(
    first_day=first_day, last_day=last_day, churned=churned
)

payments = billing_base.merge(due_dates, how='cross')
payments = payments[(payments['due_date'] >= payments['first_day']) & (payments['due_date'] <= payments['last_day'])]
payments = payments.reset_index(drop=True)

# customers who cancel and boleto payers pay late more often
late_prob = np.where(payments['churned'], 0.25, 0.08) + np.where(payments['payment_method'] == 'Boleto', 0.05, 0)
is_late = np.random.rand(len(payments)) < late_prob

days_early = np.random.randint(0, 4, len(payments))
days_late = np.random.randint(1, 31, len(payments))
days_after_due = np.where(is_late, days_late, -days_early)

payments['payment_date'] = payments['due_date'] + pd.to_timedelta(days_after_due, unit='D')

# some late invoices are never paid, and payments after the end of the window are not recorded yet
never_paid = is_late & (np.random.rand(len(payments)) < 0.15)
payments['payment_date'] = payments['payment_date'].where(~never_paid)
payments['payment_date'] = payments['payment_date'].where(payments['payment_date'] <= end_date)

payments['amount'] = payments['monthly_fee']

payments = payments[['customer_id', 'due_date', 'payment_date', 'amount']].sort_values(['due_date', 'customer_id'])
payments = payments.reset_index(drop=True)
payments.insert(0, 'invoice_id', range(1, len(payments) + 1))

payments.to_csv('payments.csv', index=False)
print('payments.csv created:', payments.shape)


###### Sujando a base de dados ######

# customers: null states and fees, different spellings, impossible dates and duplicated rows
state_null_idx = customers.sample(frac=0.03, random_state=1).index
customers.loc[state_null_idx, 'state'] = np.nan

fee_null_idx = customers.sample(frac=0.02, random_state=2).index
customers.loc[fee_null_idx, 'monthly_fee'] = np.nan

payment_idx = customers.sample(n=60, random_state=3).index
customers.loc[payment_idx[:30], 'payment_method'] = customers.loc[payment_idx[:30], 'payment_method'].str.upper()
customers.loc[payment_idx[30:], 'payment_method'] = customers.loc[payment_idx[30:], 'payment_method'] + ' '

canceled_idx = customers[customers['cancel_date'].notna()].sample(n=10, random_state=4).index
customers.loc[canceled_idx, 'cancel_date'] = customers.loc[canceled_idx, 'signup_date'] - pd.Timedelta(days=30)

customers = pd.concat([customers, customers.sample(n=20, random_state=5)], ignore_index=True)

# tickets: reasons written in different ways and duplicated rows
reason_idx = tickets.sample(n=60, random_state=6).index
tickets.loc[reason_idx[:30], 'reason'] = tickets.loc[reason_idx[:30], 'reason'].str.lower()
tickets.loc[reason_idx[30:], 'reason'] = tickets.loc[reason_idx[30:], 'reason'].str.upper()

tickets = pd.concat([tickets, tickets.sample(n=30, random_state=7)], ignore_index=True)

# payments: duplicated rows
payments = pd.concat([payments, payments.sample(n=50, random_state=8)], ignore_index=True)

# saving the dirty files (overwrites the clean ones)
customers.to_csv('customers.csv', index=False)
tickets.to_csv('tickets.csv', index=False)
payments.to_csv('payments.csv', index=False)

print('dirty customers.csv:', customers.shape)
print('dirty tickets.csv:', tickets.shape)
print('dirty payments.csv:', payments.shape)

