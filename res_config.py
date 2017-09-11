from openerp.osv import fields, osv
from openerp.tools.translate import _


class quality_config_settings(osv.osv_memory):
    _name = 'quality.config.settings'
    _inherit = 'res.config.settings'
    
    
    _columns={
	    'group_quality_adv_location': fields.selection([
		    (0, 'No automatic routing of products'),
		    (1, 'Advanced routing of products using rules')
		    ], "Routes",
		    implied_group='stock.group_adv_location',
		    help="""This option supplements the warehouse application by effectively implementing Push and Pull inventory flows through Routes."""),
            }
