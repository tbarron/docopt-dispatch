import pdb
from pytest import raises, yield_fixture as fixture

from docopt_dispatch import Dispatch, DispatchError


class OptionMarker(Exception):
    pass


class ArgumentMarker(Exception):
    pass


doc = 'usage: prog [--option] [<argument>]'


@fixture
def dispatch():
    dispatch = Dispatch()

    @dispatch.on('--option')
    def option(**kwargs):
        raise OptionMarker(kwargs)

    @dispatch.on('<argument>')
    def argument(**kwargs):
        raise ArgumentMarker(kwargs)

    yield dispatch


def test_dispatch_can_dispatch_on_option(dispatch):
    with raises(OptionMarker) as error:
        dispatch(doc, '--option')
    assert error.value.args[0] == {'option': True, 'argument': None}


def test_dispatch_can_dispatch_on_argument(dispatch):
    with raises(ArgumentMarker) as error:
        dispatch(doc, 'hi')
    assert error.value.args[0] == {'option': False, 'argument': 'hi'}


def test_dispatch_will_raise_error_if_it_cannot_dispatch(dispatch):
    with raises(DispatchError) as error:
        dispatch(doc, '')
    message = ('None of dispatch conditions --option, <argument> '
               'is triggered')
    assert error.value.args[0] == message


class MultipleDispatchMarker(Exception):
    pass


@fixture
def multiple_dispatch():
    dispatch = Dispatch()

    @dispatch.on('--option', '<argument>')
    def option_argument(**kwargs):
        raise MultipleDispatchMarker(kwargs)

    yield dispatch


def test_multiple_dispatch(multiple_dispatch):
    with raises(MultipleDispatchMarker) as error:
        multiple_dispatch(doc, 'hi --option')
    assert error.value.args[0] == {'option': True, 'argument': 'hi'}


def test_multiple_dispatch_will_raise_error(multiple_dispatch):
    with raises(DispatchError) as error:
        multiple_dispatch(doc, '--option')
    message = ('None of dispatch conditions --option <argument> '
               'is triggered')
    assert error.value.args[0] == message


def test_multiple_dispatch_will_raise_error_noopt(multiple_dispatch):
    with raises(DispatchError) as error:
        multiple_dispatch(doc, 'flipper')
    message = ('None of dispatch conditions --option <argument> '
               'is triggered')
    assert error.value.args[0] == message


ordoc = """
Usage:
    cli
    cli parse --all
    cli parse [URL]
"""

class OrderDispatchMarker(Exception):
    pass


@fixture
def order_dispatch():
    dispatch = Dispatch()

    @dispatch.on()
    def bare(**kwargs):
        result = kwargs.copy()
        result['function'] = 'bare'
        raise OrderDispatchMarker(result)

    @dispatch.on('parse')
    def cmd(**kwargs):
        result = kwargs.copy()
        result['function'] = 'cmd'
        raise OrderDispatchMarker(result)

    @dispatch.on('parse', 'URL')
    def arg(**kwargs):
        result = kwargs.copy()
        result['function'] = 'arg'
        raise OrderDispatchMarker(result)

    @dispatch.on('parse', '--all')
    def opt(**kwargs):
        result = kwargs.copy()
        result['function'] = 'opt'
        raise OrderDispatchMarker(result)

    yield dispatch


def test_order_bare(order_dispatch):
    with raises(OrderDispatchMarker) as error:
        order_dispatch(ordoc, "")
    assert error.value.args[0] == {'parse': False, 'all': False, 'URL': None,
                                   'function': 'bare',}


def test_order_cmd(order_dispatch):
    with raises(OrderDispatchMarker) as error:
        order_dispatch(ordoc, "parse")
    assert error.value.args[0] == {'parse': True, 'all': False, 'URL': None,
                                   'function': 'cmd'}


def test_order_url(order_dispatch):
    with raises(OrderDispatchMarker) as error:
        order_dispatch(ordoc, "parse url")
    assert error.value.args[0] == {'parse': True, 'all': False, 'URL': 'url',
                                   'function': 'arg'}


def test_order_all(order_dispatch):
    with raises(OrderDispatchMarker) as error:
        order_dispatch(ordoc, "parse --all")
    assert error.value.args[0] == {'parse': True, 'all': True, 'URL': None,
                                   'function': 'opt'}

