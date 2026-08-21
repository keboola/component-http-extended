'''
Created on 12. 11. 2018

@author: esner
'''
import unittest
import mock
import os
import json
import tempfile
import requests
from freezegun import freeze_time

from component import Component, UserException


def _build_data_dir(base_dir, parameters):
    """
    Creates a minimal KBC data directory with the given parameters and returns its path.
    """
    os.makedirs(os.path.join(base_dir, 'out', 'files'))
    with open(os.path.join(base_dir, 'config.json'), 'w') as cfg:
        json.dump({'parameters': parameters, 'image_parameters': {}}, cfg)
    return base_dir


def _mock_response(status_code, reason, content=b''):
    """
    Builds a requests.Response-like mock that mimics raise_for_status() for the given status code.
    """
    response = mock.MagicMock()
    response.status_code = status_code
    response.reason = reason
    response.iter_content.return_value = [content] if content else []
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            F'{status_code} Client Error: {reason} for url: https://example.com/file.csv', response=response)
    else:
        response.raise_for_status.return_value = None
    return response


class TestComponent(unittest.TestCase):

    # set global time to 2010-10-10 - affects functions like datetime.now()
    @freeze_time("2010-10-10")
    # set KBC_DATADIR env to non-existing dir
    @mock.patch.dict(os.environ, {'KBC_DATADIR': './non-existing-dir'})
    def test_run_no_cfg_fails(self):
        with self.assertRaises(ValueError):
            comp = Component()
            comp.run()


class TestHttpErrorHandling(unittest.TestCase):
    """
    Regression tests for the defensive handling of failed HTTP responses.
    """

    PARAMETERS = {'path': 'https://example.com/file.csv', 'file_name': 'file.csv'}

    def _run_with_response(self, response):
        """
        Runs the component against a mocked HTTP response and returns the bytes written to the output file
        (None when no output file was produced).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = _build_data_dir(tmp_dir, self.PARAMETERS)
            with mock.patch.dict(os.environ, {'KBC_DATADIR': data_dir}):
                with mock.patch('component.requests.get', return_value=response):
                    comp = Component()
                    comp.run()
            res_file_path = os.path.join(data_dir, 'out', 'files', self.PARAMETERS['file_name'])
            if not os.path.isfile(res_file_path):
                return None
            with open(res_file_path, 'rb') as res_file:
                return res_file.read()

    def test_client_error_raises_user_exception(self):
        """A 4xx is the user's problem (wrong URL / credentials) - it must fail as a user error."""
        with self.assertRaises(UserException) as ctx:
            self._run_with_response(_mock_response(404, 'Not Found'))

        message = str(ctx.exception)
        self.assertIn('404', message)
        self.assertIn('Not Found', message)
        self.assertIn(self.PARAMETERS['path'], message)

    def test_client_error_chains_original_http_error(self):
        """The original requests exception is kept as the cause, so nothing is lost from the log."""
        with self.assertRaises(UserException) as ctx:
            self._run_with_response(_mock_response(401, 'Unauthorized'))

        self.assertIsInstance(ctx.exception.__cause__, requests.exceptions.HTTPError)

    def test_server_error_still_raises_http_error(self):
        """Non-4xx failures must keep behaving exactly as before - raw HTTPError, application error."""
        with self.assertRaises(requests.exceptions.HTTPError):
            self._run_with_response(_mock_response(503, 'Service Unavailable'))

    def test_successful_response_is_unaffected(self):
        """The happy path must be untouched - the response body is still written to the output file."""
        self.assertEqual(b'a,b\n1,2\n', self._run_with_response(_mock_response(200, 'OK', content=b'a,b\n1,2\n')))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
