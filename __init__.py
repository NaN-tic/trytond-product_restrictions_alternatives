# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .party import *
from .sale import *


def register():
    Pool.register(
        RestrictionAlternative,
        Party,
        Sale,
        module='product_restrictions_alternatives', type_='model')
