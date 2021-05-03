
**Parameters**

- **path** – An URL of the page.
- **file_name** - result file name
- **tag** - optional tag of the file - manifest is created with `permanent=false`
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


### user_parameters

A list of user parameters that is are accessible from within headers and additional parameters. This is useful for storing
for example user credentials that are to be filled in a login form. Appending `#` sign before the attribute name will hash the value and store it securely
within the configuration (recommended for passwords). The value may be scalar or a supported function. You can access user parameters vis:

```json
"value": {
          "attr": "#token"
        }
```

### additional_requests_pars

- (OPT) additional request parameters. 

- **key** - name of the parameter (e.g. `params` to list http parameters)
- **value** - value of the parameter

**NOTE** the `'false','true'` string values are converted to boolean, objects will be treated as python dictionaries. 
`{"attr":"some_user_par"}` notation is supported to reference custom user_parameters

**Supported keys**:

- `params`: (optional) Dictionary, http query parameters to be sent with a request. e.g.
`{
        "key": "params",
        "value": {
          "date": "2020-01-01"
        }
`

- `cookies`: (optional) Dict to send with the request. e.g. `{"sessioncookie": "123456789"}`
- `timeout`: (optional) How many seconds to wait for the server to send data
        before giving up, as a float.
- `allow_redirects`: (optional) Boolean. Defaults to `True`.
- `proxies`: (optional) Dictionary mapping protocol to the URL of the proxy. e.g. 
`
{
  "http": "http://10.10.1.10:3128",
  "https": "http://10.10.1.10:1080"
}
`
- `verify`: (optional) Boolean controls whether we verify
            the server's TLS certificate, Defaults to `True`. 



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

