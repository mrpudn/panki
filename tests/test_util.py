import unittest
from datetime import datetime, timezone
import click
import panki.util


class TestUtil(unittest.TestCase):

    def test_strip_split(self):
        self.assertEqual(
            panki.util.strip_split(' a , b , c '),
            ['a', 'b', 'c']
        )

    def test_strip_lines(self):
        self.assertEqual(panki.util.strip_lines(['', '', '']), [])
        self.assertEqual(
            panki.util.strip_lines(['', 'a', '', 'b', '', 'c', '\n']),
            ['a', '', 'b', '', 'c']
        )

    def test_generate_id(self):
        self.assertWithinMilliseconds(
            datetime.now(timezone.utc).timestamp() * 1000,
            panki.util.generate_id()
        )

    def test_timestamp(self):
        self.assertWithinMilliseconds(
            datetime.now(timezone.utc).timestamp() * 1000,
            panki.util.timestamp() * 1000
        )

    def test_utcnow(self):
        self.assertWithinMilliseconds(
            datetime.now(timezone.utc).timestamp() * 1000,
            panki.util.utcnow().timestamp() * 1000
        )

    def test_bad_param(self):
        with self.assertRaises(click.BadParameter) as cm:
            panki.util.bad_param('foobar', 'foo bar baz')
        exception = cm.exception
        self.assertEqual(exception.param_hint, 'foobar')
        self.assertEqual(exception.message, 'foo bar baz')

    def test_multi_opt(self):
        self.assertEqual(
            panki.util.multi_opt(),
            dict(multiple=True, nargs=1, default=[])
        )
        self.assertEqual(
            panki.util.multi_opt(3),
            dict(multiple=True, nargs=3, default=[])
        )
        self.assertEqual(
            panki.util.multi_opt(3, ['foo', 'bar']),
            dict(multiple=True, nargs=3, default=['foo', 'bar'])
        )

    def assertWithinMilliseconds(self, timestamp1, timestamp2, ms=1000):
        self.assertTrue(timestamp1 > (timestamp2 - ms))
        self.assertTrue(timestamp1 < (timestamp2 + ms))
