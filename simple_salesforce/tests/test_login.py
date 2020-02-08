"""Tests for login.py"""

import re
import os
import warnings
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import responses
import requests
try:
    # Python 2.6/2.7
    import httplib as http
    from urlparse import urlparse
    from mock import Mock, patch
except ImportError:
    # Python 3
    import http.client as http
    from unittest.mock import Mock, patch
    from urllib.parse import urlparse

from simple_salesforce import tests
from simple_salesforce.login import SalesforceLogin
from simple_salesforce.exceptions import SalesforceAuthenticationFailed


class TestSalesforceLogin(unittest.TestCase):
    """Tests for the SalesforceLogin function"""
    def setUp(self):
        """Setup the SalesforceLogin tests"""
        request_patcher = patch('simple_salesforce.login.requests')
        self.mockrequest = request_patcher.start()
        self.addCleanup(request_patcher.stop)

    def _test_login_success(self, url_regex, salesforce_login_kwargs,
                            response_body=tests.LOGIN_RESPONSE_SUCCESS):
        """Test SalesforceLogin with one set of arguments.

        Mock login requests at url_regex, returning a successful response,
        response_body. Check that the fake-login process works when passing
        salesforce_login_kwargs as keyword arguments to SalesforceLogin in
        addition to the mocked session and a default username.
        """
        responses.add(
            responses.POST,
            url_regex,
            body=response_body,
            status=http.OK
        )
        session_state = {
            'used': False,
        }

        # pylint: disable=missing-docstring,unused-argument
        def on_response(*args, **kwargs):
            session_state['used'] = True

        session = requests.Session()
        session.hooks = {
            'response': on_response,
        }
        session_id, instance = SalesforceLogin(
            session=session,
            username='foo@bar.com',
            **salesforce_login_kwargs
        )
        self.assertTrue(session_state['used'])
        self.assertEqual(session_id, tests.SESSION_ID)
        self.assertEqual(instance, urlparse(tests.SERVER_URL).netloc)

    @responses.activate
    def test_default_domain_success(self):
        """Test default domain logic and login"""
        login_args = {'password': 'password', 'security_token': 'token'}
        self._test_login_success(re.compile(r'^https://login.*$'), login_args)

    @responses.activate
    def test_custom_domain_success(self):
        """Test custom domain login"""
        login_args = {
            'password': 'password',
            'security_token': 'token',
            'domain': 'testdomain.my'
        }
        self._test_login_success(
            re.compile(r'^https://testdomain.my.salesforce.com/.*$'),
            login_args)

    @responses.activate
    def test_deprecated_sandbox_disabled_success(self):
        """Test sandbox=False logs into login.salesforce.com."""
        login_args = {
            'password': 'password',
            'security_token': 'token',
            'sandbox': False
        }
        self._test_login_success(
            re.compile(r'^https://login.salesforce.com/.*$'), login_args)

    @responses.activate
    def test_deprecated_sandbox_enabled_success(self):
        """Test sandbox=True logs into test.salesforce.com."""
        login_args = {
            'password': 'password',
            'security_token': 'token',
            'sandbox': True
        }
        self._test_login_success(
            re.compile(r'^https://test.salesforce.com/.*$'), login_args)

    def test_domain_sandbox_mutual_exclusion_failure(self):
        """Test sandbox and domain mutual exclusion."""

        with self.assertRaises(ValueError):
            SalesforceLogin(
                username='myemail@example.com.sandbox',
                password='password',
                security_token='token',
                domain='login',
                sandbox=False
            )

    def test_failure(self):
        """Test A Failed Login Response"""
        return_mock = Mock()
        return_mock.status_code = 500
        # pylint: disable=line-too-long
        return_mock.content = '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sf="urn:fault.partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Body><soapenv:Fault><faultcode>INVALID_LOGIN</faultcode><faultstring>INVALID_LOGIN: Invalid username, password, security token; or user locked out.</faultstring><detail><sf:LoginFault xsi:type="sf:LoginFault"><sf:exceptionCode>INVALID_LOGIN</sf:exceptionCode><sf:exceptionMessage>Invalid username, password, security token; or user locked out.</sf:exceptionMessage></sf:LoginFault></detail></soapenv:Fault></soapenv:Body></soapenv:Envelope>'
        self.mockrequest.post.return_value = return_mock

        with self.assertRaises(SalesforceAuthenticationFailed):
            SalesforceLogin(
                username='myemail@example.com.sandbox',
                password='password',
                security_token='token',
                domain='test'
            )
        self.assertTrue(self.mockrequest.post.called)

    @responses.activate
    def test_token_login_success(self):
        """Test a successful JWT Token login"""
        pkey_file = os.path.join(os.path.dirname(__file__), 'sample-key.pem')
        login_args = {
            'consumer_key': '12345.abcde',
            'privatekey_file': pkey_file
        }
        self._test_login_success(
            re.compile(r'^https://login.salesforce.com/.*$'), login_args,
            response_body=tests.TOKEN_LOGIN_RESPONSE_SUCCESS)

    def test_token_login_failure(self):
        """Test a failed JWT Token login"""
        return_mock = Mock()
        return_mock.status_code = 400
        # pylint: disable=line-too-long
        return_mock.content = '{"error": "invalid_client_id", "error_description": "client identifier invalid"}'
        self.mockrequest.post.return_value = return_mock

        with self.assertRaises(SalesforceAuthenticationFailed):
            SalesforceLogin(
                username='myemail@example.com.sandbox',
                consumer_key='12345.abcde',
                privatekey_file=os.path.join(
                    os.path.dirname(__file__), 'sample-key.pem'
                )
            )
        self.assertTrue(self.mockrequest.post.called)

    @responses.activate
    def test_token_login_failure_with_warning(self):
        """Test a failed JWT Token login that also produces a helful warning"""
        responses.add(
            responses.POST,
            re.compile(r'^https://login.*$'),
            # pylint: disable=line-too-long
            body='{"error": "invalid_grant", "error_description": "user hasn\'t approved this consumer"}',
            status=400
        )
        session_state = {
            'used': False,
        }

        # pylint: disable=missing-docstring,unused-argument
        def on_response(*args, **kwargs):
            session_state['used'] = True

        session = requests.Session()
        session.hooks = {
            'response': on_response,
        }
        with warnings.catch_warnings(record=True) as warning:
            with self.assertRaises(SalesforceAuthenticationFailed):
                # pylint: disable=unused-variable
                session_id, instance = SalesforceLogin(
                    session=session,
                    username='foo@bar.com',
                    consumer_key='12345.abcde',
                    privatekey_file=os.path.join(
                        os.path.dirname(__file__), 'sample-key.pem'
                    )
                )
            assert len(warning) >= 1
            assert issubclass(warning[-1].category, UserWarning)
            assert str(warning[-1].message) == tests.TOKEN_WARNING
        self.assertTrue(session_state['used'])
