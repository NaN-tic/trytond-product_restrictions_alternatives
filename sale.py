# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale']


class Sale(metaclass=PoolMeta):
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
            if line.product and line.product.template.restrictions:
                lines.append(line)

        if not lines:
            return []

        party_alternative = (
            self.party.restriction_alternatives[0].alternative_party)
        new_sale, = self.__class__.copy([self], {
                'lines': [],
                })
        new_sale.party = party_alternative
        new_sale.on_change_party()
        new_sale.save()

        lines_to_write.extend((lines, {'sale': new_sale.id}))
        if lines_to_write:
            SaleLine.write(*lines_to_write)

        for line in lines:
            line.taxes = []
            line.on_change_product()

        if lines:
            SaleLine.save(lines)

        return [new_sale]
