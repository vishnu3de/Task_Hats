# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_batch_payroll(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'hr_batch_payroll'

    department_id = fields.Many2one('hr.department', string='Department')
    total_amount = fields.Float(string='Total Amount',compute='_compute_total_amount')
    month = fields.Char(string='Month', compute="_compute_month")

    @api.depends('date_start', 'date_end')
    def _compute_month(self):
        for rec in self:
            if rec.date_start:
                rec.month = (rec.date_start.strftime('%B'))

    @api.depends('slip_ids.line_ids.total', 'slip_ids')
    def _compute_total_amount(self):
        for record in self:
            total = 0
            for slip in record.slip_ids:
                total += sum(line.total for line in slip.line_ids)
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
        department_id = self.env['hr.employee'].search([('department_id','=',payslip_id.department_id.id)])
        res = super(HrPayslipEmployees, self).default_get(fields)
        res['employee_ids'] = [(6, 0, [emp.id for emp in department_id])]

        return res
