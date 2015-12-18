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
            new_sales.append(sale)
            new_sales.extend(sale.split_by_product_restrictions())
        super(Sale, cls).quote(new_sales)

    def split_by_product_restrictions(self):
        '''
        Returns a list of new sales with alternative parties of restricted
        products
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        new_sales = []
        products = list(set(l.product.template for l in self.lines
                if l.product))
        splits = self.party.split_by_product_restrictions(products,
            type='customer')
        linesbyproduct = defaultdict(list)
        for line in self.lines:
            if not line.product:
                continue
            linesbyproduct[line.product.template].append(line)
        if self.party in splits:
            del splits[self.party]
        to_write, lines_to_write = [], []
        for party, products in splits.iteritems():
            new_sale, = self.__class__.copy([self], {
                    'lines': [],
                    })
            new_sale.party = party
            for key, value in new_sale.on_change_party().iteritems():
                setattr(new_sale, key, value)
            to_write.extend(([new_sale], new_sale._save_values))
            new_sale.save()

            lines = []
            for product in products:
                lines.extend(linesbyproduct[product])
            lines_to_write.extend((lines, {'sale': new_sale.id}))
            new_sales.append(new_sale)
        if to_write:
            Sale.write(*to_write)
        if lines_to_write:
            SaleLine.write(*lines_to_write)
        return new_sales
