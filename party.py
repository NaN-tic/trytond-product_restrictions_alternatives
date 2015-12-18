# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from collections import defaultdict
from itertools import chain
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta

__all__ = ['RestrictionAlternative', 'Party']
__metaclass__ = PoolMeta


class RestrictionAlternative(ModelSQL, ModelView):
    'Restriction Alternative'
    __name__ = 'party.restriction.alternative'
    party = fields.Many2One('party.party', 'Party', select=True, required=True,
        ondelete='CASCADE')
    sequence = fields.Integer('Sequence')
    alternative_party = fields.Many2One('party.party', 'Alternative Party',
        required=True, ondelete='CASCADE')

    @staticmethod
    def order_sequence(tables):
        table, _ = tables[None]
        return [table.sequence == None, table.sequence]


class Party:
    __name__ = 'party.party'
    restriction_alternatives = fields.One2Many('party.restriction.alternative',
        'party', 'Alternative Parties')

    def split_by_product_restrictions(self, products, type='customer'):
        '''
        Returns a dict with alternative parties as keys and the allowedi
        products as values

        The None key is used to indicate that the product is not allowed
        for any party
        '''
        parties = [self] + [p.alternative_party for p in
            self.restriction_alternatives]
        splits = defaultdict(list)
        for party in parties:
            party_restrictions = set(getattr(party, '%s_restrictions' % type))
            not_assigned = set(products) - set(chain(*splits.values()))
            for product in not_assigned:
                product_restrictions = set(product.restrictions)
                if (product_restrictions and
                        product_restrictions - party_restrictions):
                    continue
                splits[party].append(product)
        not_assigned = set(products) - set(chain(*splits.values()))
        if not_assigned:
            splits[None] = list(not_assigned)
        return dict(splits)
