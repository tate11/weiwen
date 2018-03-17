# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Enapps LTD (<http://www.enapps.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.osv import osv
from odoo import fields,models,api


class ea_import_template_line_calc_field(models.Model):
    _name = 'ea_import.template.line.calc_field'

    name=fields.Char('Name', size=64, help='Field description. Just for reference', required="1")
    template_line_id=fields.Many2one('ea_import.template.line', 'Template Line',)
    sequence=fields.Integer('Sequence', help='Order of performing')
    column_number=fields.Integer('Field number',)
    operation=fields.Selection([
            ('+', '+'),
            ('-', '-'),
            ('*', '*'),
            ('/', '/'),
        ], 'Mathematic operation', )


    _defaults = {
    }

    @api.multi
    def calculate(self,previouse_result, string_list):
        for calc_field in self:
            result = eval("%f %s %f" % (previouse_result, calc_field.operation, float(string_list[calc_field.column_number - 1].strip() or "0")))
            return result



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
