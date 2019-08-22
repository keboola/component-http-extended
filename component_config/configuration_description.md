
**Parameters**

- **path** – An URL of the page.
- **headers** - Array of HTTP headers to send. You may include User parameters as a value
```json
"headers": [
      {
        "key": "Authorization",
        "value": {
          "attr": "#token"
        }
      }
    ]
```

- **additional_requests_pars** - (OPT) additional kwarg parameters that are accepted by the 
Python [Requests library](https://2.python-requests.org/en/master/user/quickstart/#make-a-request), get method. 
**NOTE** the `'false','true'` string values are converted to boolean, objects will be treated as python dictionaries
```json
"additional_requests_pars": [
      {
        "key": "verify",
        "value": "false"
      },
      {
        "key": "params",
        "value": {
          "date": {
            "attr": "date"
          }
        }
      }
    ]
```
- **user_parameters** – A list of user parameters that is are accessible from within headers and additional parameters. This is useful for storing
for example user credentials that are to be filled in a login form. Appending `#` sign before the attribute name will hash the value and store it securely
within the configuration (recommended for passwords). The value may be scalar or a supported function. You can access user parameters vis:
```json
"value": {
          "attr": "#token"
        }
```
