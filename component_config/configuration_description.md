
**Parameters**

- **path** – An URL of the page.
- **headers** - Array of HTTP headers to send. You may include User parameters as a value
```json
"headers": [
      {__
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

## Configruation example

```json
{
    "path": "https://example.com",
    "file_name": "test.csv",
    "user_parameters": {
      "#token": "Bearer xxx",
      "date": {
        "function": "concat",
        "args": [
          {
            "function": "string_to_date",
            "args": [
              "yesterday",
              "%Y-%m-%d"
            ]
          },
          "T"
        ]
      }
    },
    "headers": [
      {
        "key": "Authorization",
        "value": {
          "attr": "#token"
        }
      }
    ],
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
    ],
    "debug": true
  }
```

The above will call GET `https://example.com/?date=2019-08-21T` with header `Authorization: Bearer xxx`

Actually by calling `requests.get(headers={'Authorization': 'Bearer xxx'}, params={'date':'2019-08-21T'}`

