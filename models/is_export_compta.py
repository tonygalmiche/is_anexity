# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import codecs
import unicodedata
import base64


class IsExportComptaLigne(models.Model):
    _name = 'is.export.compta.ligne'
    _description = u"Export Compta Lignes"
    _order='ligne,id'

    export_compta_id   = fields.Many2one('is.export.compta', 'Export Compta', required=True, ondelete='cascade')
    ligne              = fields.Integer("Ligne")
    entite             = fields.Char("Entité")
    code_journal       = fields.Char("Code journal")
    libelle_journal    = fields.Char("Libellé journal")
    num_compte         = fields.Char("Numéro de compte")
    libelle_compte     = fields.Char("Libellé du compte")
    compte_auxiliaire  = fields.Char("Numéro de compte auxiliaire")
    libelle_auxiliaire = fields.Char("Libellé du compte auxiliaire")
    num_piece          = fields.Char("Numéro de la pièce")
    axe_analytique     = fields.Char("Axe analytique")
    date_piece         = fields.Char("Date de la pièce")
    date_echeance      = fields.Char("Date d'échéance")
    debit              = fields.Float("Debit" , digits=(14,2))
    credit             = fields.Float("Credit", digits=(14,2))
    contrat            = fields.Char("Contrat")
    move_id            = fields.Many2one('account.move', 'Facture')





class IsExportCompta(models.Model):
    _name = 'is.export.compta'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Export Compta"
    _order = 'name desc'

    name       = fields.Char("N°Folio", readonly=True)
    date_fin   = fields.Date("Date de fin", required=True)
    ligne_ids  = fields.One2many('is.export.compta.ligne', 'export_compta_id', 'Lignes')
    file_ids   = fields.Many2many('ir.attachment', 'is_export_compta_attachment_rel', 'doc_id', 'file_id', 'Fichiers')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('is.export.compta')
        res = super(IsExportCompta, self).create(vals)
        return res


    def generer_lignes_action(self):
        cr=self._cr
        for obj in self:
            print(obj)

            invoices = self.env['account.move'].search([('is_export_compta_id','=',obj.id)])
            for invoice in invoices:
                invoice.is_export_compta_id=False
            obj.ligne_ids.unlink()

            filtre=[
                ('is_export_compta_id','=',False),
                ('invoice_date','<=',obj.date_fin),
                ('state', '=', 'posted'),
                ('journal_id.code','=','FAC'),
                #('id','in',[1981,1842]),
            ]

            invoices = self.env['account.move'].search(filtre,order="name")
            ligne=0
            for invoice in invoices:
                invoice.is_export_compta_id = obj.id
                print(invoice.name)
                for line in invoice.line_ids:
                    if line.account_id:
                        ligne+=1
                        libelle_auxiliaire = (invoice.partner_id.parent_id.name or invoice.partner_id.name or '')
                        print(line.display_type,invoice.name,line.account_id.code,line.debit,line.credit,line.date_maturity,invoice.invoice_date_due)
                        vals={
                            'export_compta_id'  : obj.id,
                            'ligne'             : ligne,
                            'entite'            : 'ANEXITI',
                            'code_journal'      : 'VTE',
                            'libelle_journal'   : 'Journal de vente',
                            'num_compte'        : line.account_id.code,
                            'libelle_compte'    : line.account_id.name,
                            'compte_auxiliaire' : (invoice.partner_id.parent_id.ref or invoice.partner_id.ref),
                            'libelle_auxiliaire': libelle_auxiliaire,
                            'num_piece'         : invoice.name,
                            'axe_analytique'    : invoice.x_studio_analytique,
                            'date_piece'        : invoice.invoice_date,
                            'date_echeance'     : invoice.invoice_date_due,
                            'debit'             : line.debit,
                            'credit'            : line.credit,
                            'contrat'           : libelle_auxiliaire+' '+(invoice.invoice_origin or ''),
                            'move_id'           : invoice.id,
                        }
                        self.env['is.export.compta.ligne'].create(vals)


    def generer_fichier_action(self):
        cr=self._cr
        for obj in self:
            print(obj)
            name='export-compta.csv'
            model='is.export.compta'
            attachments = self.env['ir.attachment'].search([('res_model','=',model),('res_id','=',obj.id),('name','=',name)])
            attachments.unlink()
            dest     = '/tmp/'+name
            f = codecs.open(dest,'wb',encoding='utf-8')
            f.write("Entité\tCode journal\tLibellé journal\tNuméro de compte\tLibellé du compte\tNuméro de compte auxiliaire\tLibellé du compte auxiliaire\tNuméro de la pièce\tAxe analytique\tDate de la pièce\tDate d'échéance\tDébit\tCrédit\tContrat\r\n")
            for row in obj.ligne_ids:
                f.write(str(row.entite)+'\t')
                f.write(str(row.code_journal)+'\t')
                f.write(str(row.libelle_journal)+'\t')
                f.write(str(row.num_compte)+'\t')
                f.write(str(row.libelle_compte)+'\t')
                f.write(str(row.compte_auxiliaire)+'\t')
                f.write(str(row.libelle_auxiliaire)+'\t')
                f.write(str(row.num_piece)+'\t')
                f.write(str(row.axe_analytique)+'\t')
                f.write(str(row.date_piece)+'\t')
                f.write(str(row.date_echeance)+'\t')
                f.write(str(row.debit)+'\t')
                f.write(str(row.credit)+'\t')
                f.write(str(row.contrat)+'\r\n')
            f.close()
            r = open(dest,'rb').read()
            r=base64.b64encode(r)
            vals = {
                'name':        name,
                #'datas_fname': name,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       r,
            }
            attachment = self.env['ir.attachment'].create(vals)
            obj.file_ids=[(6,0,[attachment.id])]


