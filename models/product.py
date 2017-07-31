# -*- coding: utf-8 -*-
# copyright reserved

from openerp.osv import fields, osv
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

    	
class productProduct(models.Model):
    _inherit='product.product'
   
    @api.v7
    def _get_domain_locations(self,cr, uid, ids, context=None):
        '''
        Parses the context and returns a list of location_ids based on it.
        It will return all stock locations when no parameters are given
        Possible parameters are shop, warehouse, location, force_company, compute_child
        '''
        context = context or {}

        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')

        location_ids = []
        if context.get('location', False):
            if isinstance(context['location'], (int, long)):
                location_ids = [context['location']]
            elif isinstance(context['location'], basestring):
                domain = [('complete_name','ilike',context['location'])]
                if context.get('force_company', False):
                    domain += [('company_id', '=', context['force_company'])]
                location_ids = location_obj.search(cr, uid, domain, context=context)
            else:
                location_ids = context['location']
        else:
            if context.get('warehouse', False):
                if isinstance(context['warehouse'], (int, long)):
                    wids = [context['warehouse']]
                elif isinstance(context['warehouse'], basestring):
                    domain = [('name', 'ilike', context['warehouse'])]
                    if context.get('force_company', False):
                        domain += [('company_id', '=', context['force_company'])]
                    wids = warehouse_obj.search(cr, uid, domain, context=context)
                else:
                    wids = context['warehouse']
            else:
                wids = warehouse_obj.search(cr, uid, [], context=context)

            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.view_location_id.id)
    
    
        operator = context.get('compute_child', True) and 'child_of' or 'in'
        domain = context.get('force_company', False) and ['&', ('company_id', '=', context['force_company'])] or []
        locations = location_obj.browse(cr, uid, location_ids, context=context)
        loc_id=self.pool.get('stock.location').search(cr,uid,[('quality_ck_loc','!=',True)])
        if operator == "child_of" and locations and locations[0].parent_left != 0:
            loc_domain = []
            dest_loc_domain = []
            for loc in locations:
                if loc_domain:
                    loc_domain = ['|'] + loc_domain  + ['&', ('location_id.parent_left', '>=', loc.parent_left), ('location_id.parent_left', '<', loc.parent_right)]
                    dest_loc_domain = ['|'] + dest_loc_domain + ['&', ('location_dest_id.parent_left', '>=', loc.parent_left), ('location_dest_id.parent_left', '<', loc.parent_right)]
                else:
                    loc_domain += ['&', ('location_id.parent_left', '>=', loc.parent_left), ('location_id.parent_left', '<', loc.parent_right)]
                    dest_loc_domain += ['&', ('location_dest_id.parent_left', '>=', loc.parent_left), ('location_dest_id.parent_left', '<', loc.parent_right)]
	    
            return (
                domain + [('location_id','in',loc_id)],
                domain + ['&'] + dest_loc_domain + ['!'] + loc_domain,
                domain + ['&'] + loc_domain + ['!'] + dest_loc_domain
            )
        else:
            return (
                #domain + [('location_id', operator, location_ids)],
                domain + [('location_id','in',loc_id)],
                domain + ['&', ('location_dest_id', operator, location_ids), '!', ('location_id', operator, location_ids)],
                domain + ['&', ('location_id', operator, location_ids), '!', ('location_dest_id', operator, location_ids)]
            )


