'''
Template Component main class.

'''

import json
import logging
import os
import sys

import requests
from kbc.env_handler import KBCEnvHandler
from nested_lookup import nested_lookup

# global constants
SUPPORTED_ENDPOINTS = ['companies', 'deals']

# configuration variables
KEY_USER_PARS = 'user_parameters'
KEY_PATH = 'path'
KEY_HEADERS = 'headers'
KEY_ADDITIONAL_PARS = 'additional_requests_pars'
KEY_RES_FILE_NAME = 'file_name'

MANDATORY_PARS = [KEY_PATH, KEY_RES_FILE_NAME]
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        # override debug from config
        if self.cfg_params.get('debug'):
            debug = True

        self.set_default_logger('DEBUG' if debug else 'INFO')
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validate_config(MANDATORY_PARS)
            self.validate_image_parameters(MANDATORY_IMAGE_PARS)
        except ValueError as e:
            logging.error(e)
            exit(1)

        # intialize instance parameteres
        self.user_functions = Component.UserFunctions(self)

    def run(self):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa

        headers_cfg = params.get(KEY_HEADERS, {})

        if headers_cfg and not isinstance(headers_cfg, list):
            raise ValueError("Headers parameters is not a list of headers, edit your configuration")

        additional_params_cfg = params.get(KEY_ADDITIONAL_PARS, [])
        users_params = params.get(KEY_USER_PARS, [])

        if headers_cfg:
            headers_cfg = self._fill_in_user_parameters(headers_cfg, users_params)

        if additional_params_cfg:
            additional_params_cfg = self._fill_in_user_parameters(additional_params_cfg, users_params)

        headers = dict()
        if params.get(KEY_HEADERS):
            for h in headers_cfg:
                headers[h["key"]] = h["value"]
        additional_params = dict()
        if additional_params_cfg:
            for h in additional_params_cfg:
                # convert boolean
                val = h["value"]
                if isinstance(val, str) and val.lower() in ['false', 'true']:
                    val = val.lower() in ['true']
                additional_params[h["key"]] = val

        additional_params['headers'] = headers

        res = requests.get(params[KEY_PATH], **additional_params)
        res.raise_for_status()

        with open(os.path.join(self.data_path, 'out', 'files', params[KEY_RES_FILE_NAME]), 'w+') as out:
            out.write(res.text)

        logging.info("Extraction finished")

    def _fill_in_user_parameters(self, conf_objects, user_param):
        # convert to string minified
        steps_string = json.dumps(conf_objects, separators=(',', ':'))
        # dirty and ugly replace
        for key in user_param:
            if isinstance(user_param[key], dict):
                # in case the parameter is function, validate, execute and replace value with result
                user_param[key] = self._perform_custom_function(key, user_param[key])

            lookup_str = '{"attr":"' + key + '"}'
            steps_string = steps_string.replace(lookup_str, '"' + str(user_param[key]) + '"')
        new_steps = json.loads(steps_string)
        non_matched = nested_lookup('attr', new_steps)

        if non_matched:
            raise ValueError(
                'Some user attributes [{}] specified in configuration '
                'are not present in "user_parameters" field.'.format(non_matched))
        return new_steps

    def _perform_custom_function(self, key, function_cfg):
        if not function_cfg.get('function'):
            raise ValueError(
                F'The user parameter {key} value is object and is not a valid function object: {function_cfg}')
        new_args = []
        for arg in function_cfg.get('args'):
            if isinstance(arg, dict):
                arg = self._perform_custom_function(key, arg)
            new_args.append(arg)
        function_cfg['args'] = new_args

        return self.user_functions.execute_function(function_cfg['function'], *function_cfg.get('args'))

    class UserFunctions:
        """
        Custom function to be used in configruation
        """

        def __init__(self, component: KBCEnvHandler):
            # get access to the environment
            self.kbc_env = component

        def validate_function_name(self, function_name):
            supp_functions = self.get_supported_functions()
            if function_name not in self.get_supported_functions():
                raise ValueError(
                    F"Specified user function [{function_name}] is not supported! "
                    F"Supported functions are {supp_functions}")

        @staticmethod
        def get_supported_functions():
            return [method_name for method_name in dir(Component.UserFunctions)
                    if callable(getattr(Component.UserFunctions, method_name)) and not method_name.startswith('__')]

        def execute_function(self, function_name, *pars):
            self.validate_function_name(function_name)
            return getattr(Component.UserFunctions, function_name)(self, *pars)

        def string_to_date(self, date_string, date_format='%Y-%m-%d'):
            start_date, end_date = self.kbc_env.get_date_period_converted(date_string, date_string)
            return start_date.strftime(date_format)

        def concat(self, *args):
            return ''.join(args)


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(2)