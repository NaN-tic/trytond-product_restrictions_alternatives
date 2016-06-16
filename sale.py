# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from collections import defaultdict
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    @classmethod
    def quote(cls, sales):
        new_sales = []
        for sale in sales:
            if sale.party.restriction_alternatives:
                new_sales.extend(sale.split_by_product_restrictions())
            if not sale.lines:
                cls.delete([sale])
            else:
                new_sales.append(sale)
        super(Sale, cls).quote(new_sales)

    def split_by_product_restrictions(self):
        pool = Pool()
        SaleLine = pool.get('sale.line')

        lines, lines_to_write = [], []
        for line in self.lines:
            if line.product and not line.product.restrictions:
                lines.append(line)

        if not lines:
            return []

        new_sale, = self.__class__.copy([self], {
                'lines': [],
                })
        alternative = self.party.restriction_alternatives[0]
        new_sale.party = alternative.alternative_party.id
        for key, value in new_sale.on_change_party().iteritems():
            setattr(new_sale, key, value)
        new_sale.save()

        lines_to_write.extend((lines, {'sale': new_sale.id}))
        if lines_to_write:
            SaleLine.write(*lines_to_write)

        lines_to_write, values = [], []
        for line in lines:
            tax2remove = [l.id for l in line.taxes]
            line_vals = line.on_change_product()
            values ={
                'taxes': [
                    ('remove', tax2remove),
                    ('add', line_vals['taxes'])]
                }
            lines_to_write.extend(([line], values))

        if lines_to_write:
            SaleLine.write(*lines_to_write)

        return [new_sale]
