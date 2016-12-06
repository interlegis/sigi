# -*- coding: utf-8 -*-
import pytest

from smart_if import And, Equals, Greater, GreaterOrEqual, IfParser, In, Or


class TestVar(object):

    """
    A basic self-resolvable object similar to a Django template variable. Used
    to assist with tests.
    """

    def __init__(self, value):
        self.value = value

    def resolve(self, context):
        return self.value


class TestIfParser(IfParser):

    def create_var(self, value):
        return TestVar(value)


class ValueHolder(object):
    pass

VALORES = ValueHolder()
VALORES.true = TestVar(True)
VALORES.false = TestVar(False)
VALORES.high = TestVar(9000)
VALORES.low = TestVar(1)


def assertCalc(calc, context=None):
    """
    Test a calculation is True, also checking the inverse "negate" case.
    """
    context = context or {}
    assert calc.resolve(context)
    calc.negate = not calc.negate
    assert not calc.resolve(context)


def assertCalcFalse(calc, context=None):
    """
    Test a calculation is False, also checking the inverse "negate" case.
    """
    context = context or {}
    assert not calc.resolve(context)
    calc.negate = not calc.negate
    assert calc.resolve(context)


def test_or():
    assertCalc(Or(VALORES.true))
    assertCalcFalse(Or(VALORES.false))
    assertCalc(Or(VALORES.true, VALORES.true))
    assertCalc(Or(VALORES.true, VALORES.false))
    assertCalc(Or(VALORES.false, VALORES.true))
    assertCalcFalse(Or(VALORES.false, VALORES.false))


def test_and():
    assertCalc(And(VALORES.true, VALORES.true))
    assertCalcFalse(And(VALORES.true, VALORES.false))
    assertCalcFalse(And(VALORES.false, VALORES.true))
    assertCalcFalse(And(VALORES.false, VALORES.false))


def test_equals():
    assertCalc(Equals(VALORES.low, VALORES.low))
    assertCalcFalse(Equals(VALORES.low, VALORES.high))


def test_greater():
    assertCalc(Greater(VALORES.high, VALORES.low))
    assertCalcFalse(Greater(VALORES.low, VALORES.low))
    assertCalcFalse(Greater(VALORES.low, VALORES.high))


def test_greater_or_equal():
    assertCalc(GreaterOrEqual(VALORES.high, VALORES.low))
    assertCalc(GreaterOrEqual(VALORES.low, VALORES.low))
    assertCalcFalse(GreaterOrEqual(VALORES.low, VALORES.high))


def test_in():
    list_ = TestVar([1, 2, 3])
    invalid_list = TestVar(None)
    assertCalc(In(VALORES.low, list_))
    assertCalcFalse(In(VALORES.low, invalid_list))


def test_parse_bits():
    var = TestIfParser([True]).parse()
    assert var.resolve({})
    var = TestIfParser([False]).parse()
    assert not var.resolve({})

    var = TestIfParser([False, 'or', True]).parse()
    assert var.resolve({})

    var = TestIfParser([False, 'and', True]).parse()
    assert not var.resolve({})

    var = TestIfParser(['not', False, 'and', 'not', False]).parse()
    assert var.resolve({})

    var = TestIfParser(['not', 'not', True]).parse()
    assert var.resolve({})

    var = TestIfParser([1, '=', 1]).parse()
    assert var.resolve({})

    var = TestIfParser([1, 'not', '=', 1]).parse()
    assert not var.resolve({})

    var = TestIfParser([1, 'not', 'not', '=', 1]).parse()
    assert var.resolve({})

    var = TestIfParser([1, '!=', 1]).parse()
    assert not var.resolve({})

    var = TestIfParser([3, '>', 2]).parse()
    assert var.resolve({})

    var = TestIfParser([1, '<', 2]).parse()
    assert var.resolve({})

    var = TestIfParser([2, 'not', 'in', [2, 3]]).parse()
    assert not var.resolve({})

    var = TestIfParser([1, 'or', 1, '=', 2]).parse()
    assert var.resolve({})


def test_boolean():
    var = TestIfParser([True, 'and', True, 'and', True]).parse()
    assert var.resolve({})
    var = TestIfParser([False, 'or', False, 'or', True]).parse()
    assert var.resolve({})
    var = TestIfParser([True, 'and', False, 'or', True]).parse()
    assert var.resolve({})
    var = TestIfParser([False, 'or', True, 'and', True]).parse()
    assert var.resolve({})

    var = TestIfParser([True, 'and', True, 'and', False]).parse()
    assert not var.resolve({})
    var = TestIfParser([False, 'or', False, 'or', False]).parse()
    assert not var.resolve({})
    var = TestIfParser([False, 'or', True, 'and', False]).parse()
    assert not var.resolve({})
    var = TestIfParser([False, 'and', True, 'or', False]).parse()
    assert not var.resolve({})


def test_invalid():
    pytest.raises(ValueError, TestIfParser(['not']).parse)
    pytest.raises(ValueError, TestIfParser(['==']).parse)
    pytest.raises(ValueError, TestIfParser([1, 'in']).parse)
    pytest.raises(ValueError, TestIfParser([1, '>', 'in']).parse)
    pytest.raises(ValueError, TestIfParser([1, '==', 'not', 'not']).parse)
    pytest.raises(ValueError, TestIfParser([1, 2]).parse)
