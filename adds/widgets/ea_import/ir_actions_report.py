# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Enapps LTD (<http://www.enapps.co.uk>).
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
import odoo.report as report
import csv
import cStringIO
import re
import odoo.netsvc as netsvc


class report_xml(models.Model):
    _name = "ir.actions.report.xml"
    _inherit = "ir.actions.report.xml"
    csv_export = fields.Boolean('CSV Export')
    export_config_id=fields.Many2one('ea_export.config', 'Export config')






class CsvExportOpenERPInterface(report.interface.report_int):
    def __init__(self, name, config_value):
        self.config_value = config_value
        if name in netsvc.Service._services:
            del netsvc.Service._services[name]

        super(CsvExportOpenERPInterface, self).__init__(name)

    def create(self, data):
        config_value = self.config_value
        config_query = config_value['config_query']
        delimiter = str(config_value['delimiter'])
        quotechar = str(config_value['quotechar'])
        header = config_value['header']
        query_type = config_value['query_type']
        active_ids = self.env.context.get('active_ids', [])
        if query_type != 'sql':
            raise osv.except_osv(('Error !'), ("Not supported yet! Use SQL instead"))

        if '%s' in config_query and 'ea_export.config' not in [self.env.context.get('active_model'), self.env.context.get('filter_model')] and active_ids:
            format_param = str(tuple(active_ids)) if len(active_ids) > 1 else ('(' + str(active_ids[0]) + ')')
            variables_count = config_query.count('%s')
            if variables_count > 1:
                format_param = tuple(format_param for variable in xrange(variables_count))

            query = config_query % format_param
        elif '%s' in config_query and 'ea_export.config' in [self.env.context.get('active_model'), self.env.context.get('filter_model')]:
            raise osv.except_osv(('Error !'), ("You can execute query with '%s' formatting from {model} model only!".format(model=config_value.get('related_model'))))
        else:
            query = config_query
        if re.match(r'CREATE|DROP|UPDATE|DELETE', query, re.IGNORECASE):
            raise osv.except_osv(('Error !'), ("Operation prohibitet!"))
        try:
            self._cr.execute(query)
        except:
            raise osv.except_osv(('Error !'), ("Invalid Query"))
        output = cStringIO.StringIO()
        csvwriter = csv.writer(output, delimiter=delimiter, quotechar=quotechar)
        if header:
            csvwriter.writerow([i[0] for i in self._cr.description])  # heading row
        out = self._cr.fetchall()
        csvwriter.writerows(out)
        output_string = output.getvalue()
        output.close()
        return output_string, 'csv'


def register_csv_exporting(report_name, config_value):
    if report_name in netsvc.Service._services:

        if isinstance(netsvc.Service._services[report_name], CsvExportOpenERPInterface):
            return
        del netsvc.Service._services[report_name]
    CsvExportOpenERPInterface(report_name, config_value)


class ir_actions_report_xml(models.Model):
    _inherit = "ir.actions.report.xml"

    @api.model
    def register_all(self):
        self._cr.execute("""SELECT report.report_name,
                    config.id as config_id,
                    config.query as config_query,
                    config.delimiter,
                    config.quotechar,
                    config.header,
                    config.query_type
                    FROM ir_act_report_xml report
                    JOIN ea_export_config config ON report.export_config_id = config.id
                    WHERE report.csv_export = 'TRUE'
                    """)
        config_values = self._cr.dictfetchall()
        for config_value in config_values:
            name = 'report.' + config_value['report_name']
            register_csv_exporting(name, config_value)
        return super(ir_actions_report_xml, self).register_all()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
