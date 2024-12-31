from odoo import models, fields, api, exceptions


class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Loans Management'

    name = fields.Char(string="Loan Name", required=True)
    bank = fields.Many2one('res.partner', string="Bank", required=True)
    amount = fields.Float(string="Loan Amount", required=True)
    management_fees = fields.Selection([('loan', 'Loan'), ('loan_interest', 'Loan + Interest')])
    management_fees_amount = fields.Float(string="Management Fees Amount",)
    interest_rate = fields.Float(string="Interest Rate (%)", required=True)
    repayment_period = fields.Selection([('monthly', 'Monthly'), ('quarterly', 'quarterly'), ('half_yearly', 'Half Yearly'), ('yearly', 'Yearly')], string="Repayment Period", required=True, )
    first_payment_date = fields.Date("First Payment Date")
    debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True)
    credit_account_id = fields.Many2one('account.account', string="Credit Account", required=True)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True,)

    total_paid = fields.Float(string="Total Paid", compute='_compute_total_paid')
    balance = fields.Float(string="Outstanding Balance", compute='_compute_balance')
    company_id = fields.Many2one('res.company', string='Loan Company', default=lambda self: self.env.user.company_id, )

    inbound_payment_ids = fields.One2many('loan.payment', 'loan_id', string="Inbound Payments",
                                        domain=[('type', '=', 'inbound')])
    outbound_payment_ids = fields.One2many('loan.payment', 'loan_id', string="Outbound Payments",
                                           domain=[('type', '=', 'outbound')])
    @api.model
    def create(self, vals):
        loan = super().create(vals)
        # Create initial inbound payment for the loan amount
        self.env['loan.payment'].create({
            'loan_id': loan.id,
            'type': 'inbound',
            'amount': loan.amount,
            'debit_account_id': loan.debit_account_id.id,
            'credit_account_id': loan.credit_account_id.id,
            'is_initial_payment': True,
        })
        return loan

    @api.depends('outbound_payment_ids.amount')
    def _compute_total_paid(self):
        for record in self:
            record.total_paid = sum(payment.amount for payment in record.outbound_payment_ids)

    @api.depends('amount', 'total_paid')
    def _compute_balance(self):
        for record in self:
            record.balance = record.amount - record.total_paid

class LoanPayment(models.Model):
    _name = 'loan.payment'
    _description = 'Loan Payments'

    loan_id = fields.Many2one('loan.loan', string="Loan", required=True)
    type = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound')
    ], string="Type", required=True, default='outbound')
    amount = fields.Float(string="Payment Amount", required=True)
    date = fields.Date(string="Payment Date", default=fields.Date.context_today)
    debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True)
    credit_account_id = fields.Many2one('account.account', string="Credit Account", required=True)
    is_initial_payment = fields.Boolean(string="Initial Payment", default=False)

    @api.model
    def create(self, vals):
        payment = super().create(vals)
        payment._create_account_payment()
        return payment

    def _create_account_payment(self):
        if self.type == 'inbound':
            payment_type = 'inbound'
            partner_type = 'supplier'
            outstanding_account = self.debit_account_id
            receivable_account = self.credit_account_id
        else:
            payment_type = 'outbound'
            partner_type = 'supplier'
            outstanding_account = self.credit_account_id
            payable_account = self.debit_account_id

        payment_vals = {
            'payment_type': payment_type,
            'partner_type': partner_type,
            'partner_id': self.loan_id.bank.id,
            'amount': self.amount,
            'journal_id': self.loan_id.journal_id.id,
            'date': self.date,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'line_ids': [
                (0, 0, {
                    'account_id': outstanding_account.id,
                    'debit': self.amount if payment_type == 'inbound' else 0,
                    'credit': self.amount if payment_type == 'outbound' else 0,
                }),
                (0, 0, {
                    'account_id': receivable_account.id if payment_type == 'inbound' else payable_account.id,
                    'debit': self.amount if payment_type == 'outbound' else 0,
                    'credit': self.amount if payment_type == 'inbound' else 0,
                }),
            ],
        }

        account_payment = self.env['account.payment'].create(payment_vals)
        account_payment.action_post()
