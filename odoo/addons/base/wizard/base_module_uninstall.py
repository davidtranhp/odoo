# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BaseModuleUninstall(models.TransientModel):
    _name = "base.module.uninstall"
    _description = "Module Uninstall"

    show_all = fields.Boolean()
    module_id = fields.Many2one(
        'ir.module.module', string="Module", required=True,
        domain=[('state', 'in', ['installed', 'to upgrade', 'to install'])],
        ondelete='cascade', readonly=True,
    )
    module_ids = fields.Many2many('ir.module.module', string="Impacted modules",
                                  compute='_compute_module_ids')
    model_ids = fields.Many2many('ir.model', string="Impacted data models",
                                 compute='_compute_model_ids')

    def _get_modules(self):
        """ Return all the modules impacted by self. """
        return self.module_id.downstream_dependencies(self.module_id)

    @api.depends('module_id', 'show_all')
    def _compute_module_ids(self):
        for wizard in self:
            modules = wizard._get_modules().sorted(lambda m: (not m.application, m.sequence))
            wizard.module_ids = modules if wizard.show_all else modules.filtered('application')

    def _get_models(self):
        """ Return the models (ir.model) to consider for the impact. """
        return self.env['ir.model'].search([('transient', '=', False)])

    @api.depends('module_ids')
    def _compute_model_ids(self):
        ir_models = self._get_models()
        ir_models_xids = ir_models._get_external_ids()
        for wizard in self:
            if wizard.module_id:
                module_names = set(wizard._get_modules().mapped('name'))

                def lost(model):
                    xids = ir_models_xids.get(model.id, ())
                    return xids and all(xid.split('.')[0] in module_names for xid in xids)

                # find the models that have all their XIDs in the given modules
                self.model_ids = ir_models.filtered(lost).sorted('name')

    @api.onchange('module_id')
    def _onchange_module_id(self):
        # if we select a technical module, show technical modules by default
        if not self.module_id.application:
            self.show_all = True

    def action_uninstall(self):
        unsupported_modules = self.env['ir.module.module'].search([
            ('state', 'in', ['installed', 'to upgrade', 'to install']),
            ('name', 'in', [
                'biz_client_medicon', 'report_xlsx', 'customer_vendor_ucs', 'bi_all_in_one_merge_orders', 'deltatech_merge',
                'deltatech_merge_product', 'studio_customization', 'account_accountant', 'timesheet_grid', 'web_studio',
                'documents', 'knowledge', 'sign', 'helpdesk', 'quality_control', 'planning', 'mrp_plm', 'sale_renting',
                'industry_fsm', 'hr_appraisal', 'approvals', 'marketing_automation', 'account_consolidation', 'appointment',
                'stock_barcode', 'delivery_ups', 'delivery_dhl', 'hr_payroll', 'delivery_fedex', 'delivery_usps', 'delivery_easypost',
                'delivery_sendcloud', 'sale_amazon', 'delivery_bpost', 'pos_settle_due', 'crm_helpdesk', 'timer', 'account_asset',
                'hr_work_entry_contract_enterprise', 'helpdesk_holidays', 'mrp_mps', 'planning_contract', 'planning_holidays',
                'purchase_mrp_workorder_quality', 'quality', 'quality_mrp', 'quality_mrp_workorder', 'mrp_workorder',
                'website_sale_dashboard', 'website_helpdesk', 'website_helpdesk_forum', 'website_helpdesk_livechat',
                'website_helpdesk_slides', 'hr_payroll_attendance', 'hr_payroll_expense', 'hr_payroll_holidays', 'hr_payroll_planning',
                'hr_work_entry_contract_attendance', 'hr_work_entry_contract_planning', 'hr_work_entry_holidays_enterprise',
                'account_3way_match', 'account_accountant_batch_payment', 'account_asset_fleet', 'account_auto_transfer',
                'account_bank_statement_import', 'account_bank_statement_import_camt', 'account_bank_statement_import_csv',
                'account_bank_statement_import_ofx', 'account_base_import', 'account_batch_payment', 'account_budget',
                'account_followup', 'account_inter_company_rules', 'account_invoice_extract', 'account_invoice_extract_purchase',
                'account_online_synchronization', 'account_predictive_bills', 'account_reports', 'account_reports_tax_reminder',
                'analytic_enterprise', 'approvals_purchase', 'approvals_purchase_stock', 'barcodes_mobile', 'base_automation_hr_contract',
                'contacts_enterprise', 'crm_enterprise', 'crm_enterprise_partner_assign', 'currency_rate_live', 'data_merge', 'data_merge_crm',
                'data_merge_helpdesk', 'data_merge_project', 'data_merge_utm', 'digest_enterprise', 'documents_account', 'documents_fleet',
                'documents_fsm', 'documents_hr', 'documents_hr_contract', 'documents_hr_holidays', 'documents_hr_payroll',
                'documents_hr_recruitment', 'documents_product', 'documents_project', 'documents_project_sale', 'documents_project_sign',
                'documents_sign', 'documents_spreadsheet', 'documents_spreadsheet_account', 'documents_spreadsheet_crm', 'event_enterprise',
                'event_sale_dashboard', 'helpdesk_fsm', 'helpdesk_fsm_report', 'helpdesk_mail_plugin', 'helpdesk_sale', 'helpdesk_sms',
                'hr_attendance_mobile', 'hr_contract_reports', 'hr_contract_salary', 'hr_contract_salary_holidays',
                'hr_contract_salary_payroll', 'hr_contract_sign', 'hr_expense_extract', 'hr_expense_predict_product',
                'hr_gantt', 'hr_holidays_gantt', 'hr_mobile', 'hr_payroll_account', 'hr_payroll_fleet', 'hr_recruitment_extract',
                'hr_recruitment_reports', 'hr_recruitment_sign', 'industry_fsm_report', 'industry_fsm_sale', 'industry_fsm_sale_report',
                'industry_fsm_sms', 'industry_fsm_stock', 'mail_enterprise', 'mail_mobile', 'marketing_automation_sms',
                'mrp_account_enterprise', 'mrp_maintenance', 'mrp_subcontracting_account_enterprise', 'mrp_subcontracting_enterprise',
                'mrp_subcontracting_quality', 'mrp_subcontracting_studio', 'mrp_workorder_expiry', 'mrp_workorder_hr',
                'mrp_workorder_hr_account', 'mrp_workorder_plm', 'planning_hr_skills', 'pos_account_reports', 'pos_enterprise',
                'pos_hr_mobile', 'project_account_asset', 'project_account_budget', 'project_enterprise', 'project_enterprise_hr',
                'project_enterprise_hr_contract', 'project_helpdesk', 'project_holidays', 'project_hr_payroll_account',
                'project_timesheet_synchro', 'purchase_enterprise', 'quality_control_worksheet', 'quality_mrp_workorder_worksheet',
                'sale_account_accountant', 'sale_enterprise', 'sale_planning', 'sale_purchase_inter_company_rules', 'sale_renting_crm',
                'sale_stock_renting', 'sale_temporal', 'sale_timesheet_account_budget', 'sale_timesheet_enterprise',
                'spreadsheet_dashboard_account_accountant', 'spreadsheet_dashboard_crm', 'spreadsheet_dashboard_documents',
                'spreadsheet_dashboard_edition', 'spreadsheet_dashboard_helpdesk', 'spreadsheet_dashboard_hr_contract',
                'spreadsheet_dashboard_mrp_account', 'spreadsheet_dashboard_sale_renting', 'spreadsheet_dashboard_stock',
                'spreadsheet_edition', 'stock_account_enterprise', 'stock_accountant', 'stock_barcode_mrp',
                'stock_barcode_mrp_subcontracting', 'stock_barcode_product_expiry', 'stock_barcode_quality_control',
                'stock_enterprise', 'timesheet_grid_holidays', 'web_cohort', 'web_enterprise', 'web_gantt', 'web_grid',
                'web_map', 'web_mobile', 'website_crm_iap_reveal_enterprise', 'website_delivery_fedex',
                'website_delivery_ups', 'website_enterprise', 'website_helpdesk_knowledge', 'website_helpdesk_slides_forum',
                'website_knowledge', 'website_sale_renting', 'website_sale_renting_comparison', 'website_sale_renting_product_configurator',
                'website_sale_renting_wishlist', 'website_sale_stock_renting', 'website_studio', 'worksheet', 'data_cleaning',
                'website_appointment', 'hr_appraisal_skills', 'hr_appraisal_contract', 'appointment_hr', 'appointment_crm',
                'appointment_sms', 'website_appointment_crm', 'biz_viettel_sinvoice_v2', 'auto_database_backup', 'yteviet_account_reports',
                'theme_loftspace', 'theme_vehicle', 'theme_bistro', 'theme_clean', 'theme_nano', 'theme_common', 'theme_bookstore',
                'viin_migrator_base', 'viin_yteviet_mig_fix',
                ]),
            ])
        return unsupported_modules.button_immediate_uninstall()
