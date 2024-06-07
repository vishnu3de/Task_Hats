# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime

class hr_batch_payroll(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'hr_batch_payroll'

    MONTH_SELECTION = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ]

    month = fields.Selection(MONTH_SELECTION, string='Month',required=True)
    department_id = fields.Many2one('hr.department', string='Department',required=True)
    total_amount = fields.Float(string='Total Amount',compute='_compute_total_amount')
    date_start = fields.Date(string='Date From', readonly=True,default=False)
    date_end = fields.Date(string='Date To', readonly=True,default=False)

    @api.onchange('month')
    def _onchange_month(self):
        if self.month:
            year = datetime.now().year
            month = int(self.month)
            _, last_day = calendar.monthrange(year, month)
            self.date_start = datetime(year, month, 1).date()
            self.date_end = datetime(year, month, last_day).date()

        if self.department_id:
            overlapping_contracts = self.env['hr.payslip.run'].search([
                ('department_id', '=', self.department_id.id),
                ('month', '=', self.month)
            ])
            if overlapping_contracts:
                raise ValidationError('A batch payslip already exists for this department and month.')

    @api.model
    def create(self, vals):

        month = vals.get('month')
        department_id = vals.get('department_id')

        if month and department_id:
            overlapping_contracts = self.env['hr.payslip.run'].search([
                ('department_id', '=', department_id),
                ('month', '=', month)
            ])
            if overlapping_contracts:
                raise ValidationError('Already a batch payslip exists for this month.')

        return (super(hr_batch_payroll, self).create(vals))


    @api.depends('slip_ids.line_ids.total', 'slip_ids')
    def _compute_total_amount(self):
        for record in self:
            total = 0
            for slip in record.slip_ids:
                for line in slip.line_ids:
                    if line.code == 'NET':
                        total += line.total
            record.total_amount = total

    def write(self, vals):
        res = super(hr_batch_payroll, self).write(vals)
        if 'slip_ids' in vals:
            self._compute_total_amount()
        return res



class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def default_get(self, fields):
        active_id = self.env.context.get('active_id', False)
        payslip_id = self.env['hr.payslip.run'].search([('id','=',active_id)])
        department_id = self.env['hr.employee'].search([
            ('department_id', '=', payslip_id.department_id.id),
            ('contract_id', '!=', False),
            ('contract_id.state', '=', 'open')
        ])

        res = super(HrPayslipEmployees, self).default_get(fields)
        res['employee_ids'] = [(6, 0, [emp.id for emp in department_id])]

        return res

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        active_id = self.env.context.get('active_id', False)
        payslip_id = self.env['hr.payslip.run'].search([('id', '=', active_id)])
        existing_payslip = self.search([
            ('employee_id', '=', vals.get('employee_id')),
            ('date_from', '=', payslip_id.date_start),
            ('date_to', '=',  payslip_id.date_end),
            ('contract_id', '=', vals.get('contract_id'))
        ])
        if existing_payslip:
            raise ValidationError('A payslip with the same employee, date range, and contract already exists.')

        return super(HrPayslip, self).create(vals)
