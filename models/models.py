from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

from itertools import groupby
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        return {
            'name': first_line.name,
            'product_uom': first_line.product_id.uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': first_line.product_id.id,
            'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
        }

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        move_vals = []
        #stock_adjustments = []
        product_entries = []  # Lista para los movimientos de entrada
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))
            
            product_code = order_lines[0].product_id.default_code
            if product_code and len(product_code) > 4 and product_code[0] in ['2', '3', '4']:
                box_code = product_code[-4:].lstrip('0')
                # Buscar la caja asociada en los productos de Odoo
                product_box = self.env['product.product'].search([('default_code', '=', box_code)], limit=1)
                if product_box:
                    move_vals.append(self._create_stock_adjustmenst(order_lines[0], order_lines,product_box))
                    product_entries.append(self._create_stock_entry(order_lines[0], order_lines, product_box))
        
        moves = self.env['stock.move'].create(move_vals)
        #adjustment_moves = self.env['stock.move'].create(stock_adjustments)
        #confirmed_adjustments = adjustment_moves._action_confirm()
        #confirmed_adjustments._add_mls_related_to_order(lines, are_qties_done=True)
        #confirmed_adjustments.picked = True
        
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)
        confirmed_moves.picked = True

        # Crear los movimientos de entrada (reposición del producto)
        entry_moves = self.env['stock.move'].create(product_entries)
        confirmed_entries = entry_moves._action_confirm()
        confirmed_entries._add_mls_related_to_order(lines, are_qties_done=True)
        confirmed_entries.picked = True
        
        
        self._link_owner_on_return_picking(lines)

    def _create_stock_adjustmenst(self, first_line, order_lines,product_box):
            #_logger.info(f"Producto pertenece a la caja: {product_box.name} ({box_code})")
            # Crear movimiento de stock para descontar de la caja
            return{
                'name': f"Ajuste caja {product_box.name}",
                'product_uom': product_box.uom_id.id,
                'picking_id': self.id,
                'picking_type_id': self.picking_type_id.id,
                'product_id': product_box.id,
                'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'company_id': self.company_id.id,
            }

    def _create_stock_entry(self, first_line, order_lines, product_box):
        """ Crea un movimiento de entrada para reponer el producto que pertenece a la caja """
        return {
            'name': f"Reposición de {first_line.product_id.name}",
            'product_uom': first_line.product_id.uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': first_line.product_id.id,
            'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
            'location_id': self.location_dest_id.id,  # Se invierten los valores de entrada/salida
            'location_dest_id': self.location_id.id,
            'company_id': self.company_id.id,
        }

        