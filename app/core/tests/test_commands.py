'''
Test custom Django management commands
'''
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2OperationalError

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    '''Test custom commands'''

    def test_wait_for_db_ready(self, patched_check):
        '''Test waiting for database: is the database ready?'''
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        '''Test of the delay for database? some kind of obstacle'''

        # listened three times, still lost as to how this works
        patched_check.side_effect = [Psycopg2OperationalError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
