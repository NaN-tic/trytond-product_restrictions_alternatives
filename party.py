# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta

__all__ = ['RestrictionAlternative', 'Party']


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


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    restriction_alternatives = fields.One2Many('party.restriction.alternative',
        'party', 'Alternative Parties')
