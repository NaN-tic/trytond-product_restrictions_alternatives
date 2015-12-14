# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
import doctest
import unittest
from trytond.transaction import Transaction
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.tests.test_tryton import doctest_setup, doctest_teardown


class TestCase(unittest.TestCase):
    'Test module'

    def setUp(self):
        trytond.tests.test_tryton.install_module(
            'product_restrictions_alternatives')

    def test0005views(self):
        'Test views'
        test_view('product_restrictions_alternatives')

    def test0006depends(self):
        'Test depends'
        test_depends()

    def test_restrictions(self):
        'Test restrictions'
        Party = POOL.get('party.party')
        Template = POOL.get('product.template')
        Restriction = POOL.get('product.restriction')
        Uom = POOL.get('product.uom')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            inflamable = Restriction(name='Inflamable Products')
            inflamable.save()
            corrosive = Restriction(name='Corrosive Products')
            corrosive.save()
            parties = Party.create([{
                        'name': 'Not Restricted Party',
                        }, {
                        'name': 'InFlamable Allowed',
                        'customer_restrictions': [('add', [inflamable.id])],
                        }, {
                        'name': 'Corrosive Allowed',
                        'customer_restrictions': [('add', [corrosive.id])],
                        }])
            free_party, inflamable_party, corrosive_party = parties
            unit, = Uom.search([('symbol', '=', 'u')])
            products = Template.create([{
                        'name': 'Free Template',
                        'default_uom': unit,
                        'list_price': Decimal(0),
                        'cost_price': Decimal(0),
                        }, {
                        'name': 'Inflamable Template',
                        'default_uom': unit,
                        'list_price': Decimal(0),
                        'cost_price': Decimal(0),
                        'restrictions': [('add', [inflamable.id])],
                        }, {
                        'name': 'Corrosive Template',
                        'default_uom': unit,
                        'list_price': Decimal(0),
                        'cost_price': Decimal(0),
                        'restrictions': [('add', [corrosive.id])],
                        }])
            free_template, inflamable_template, corrosive_template = products

            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template]), {free_party: [free_template]})

            self.assertEqual(free_party.split_by_product_restrictions(
                    [inflamable_template]), {None: [inflamable_template]})

            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template, inflamable_template]), {
                        free_party: [free_template],
                        None: [inflamable_template],
                    })
            Party.write([free_party], {
                    'restriction_alternatives': [('create', [{
                                    'sequence': 10,
                                    'alternative_party': inflamable_party.id,
                                    }, {
                                    'sequence': 20,
                                    'alternative_party': corrosive_party.id,
                                    }])],
                    })
            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template]),
                {
                    free_party: [free_template],
                    })

            self.assertEqual(free_party.split_by_product_restrictions(
                    [inflamable_template]),
                {
                    inflamable_party: [inflamable_template],
                    })

            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template, inflamable_template]),
                {
                    free_party: [free_template],
                    inflamable_party: [inflamable_template],
                     })
            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template, inflamable_template, corrosive_template]),
                {
                    free_party: [free_template],
                    inflamable_party: [inflamable_template],
                    corrosive_party: [corrosive_template],
                    })
            inflamable_party.customer_restrictions += (corrosive,)
            inflamable_party.save()

            self.assertEqual(free_party.split_by_product_restrictions(
                    [free_template, inflamable_template, corrosive_template]),
                {
                    free_party: [free_template],
                    inflamable_party: [inflamable_template,
                        corrosive_template],
                    })


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    suite.addTests(doctest.DocFileSuite('scenario_sale_alternatives.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
