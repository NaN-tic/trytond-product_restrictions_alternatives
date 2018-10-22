# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import party
from . import sale

def register():
    Pool.register(
        party.RestrictionAlternative,
        party.Party,
        module='product_restrictions_alternatives', type_='model')
    Pool.register(
        sale.Sale,
        depends=['sale'],
        module='product_restrictions_alternatives', type_='model')
