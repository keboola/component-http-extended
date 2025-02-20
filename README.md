# Simple HTTP ex that allows hashed custom user paras and headers

## Configuration 

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

A list of user parameters that is are accessible from within `headers`, `additional_requests_pars` and `path`. This is useful for storing
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


**Example:**

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




### Dynamic Functions

The application support functions that may be applied on parameters in the configuration to get dynamic values.

Currently these functions work only in the `user_parameters` scope. Place the required function object instead of the user parameter value.

**Function object**

```json
{ "function": "string_to_date",
                "args": [
                  "yesterday",
                  "%Y-%m-%d"
                ]
              }
```

**Function Nesting**

Nesting of functions is supported:

```json
{
   "user_parameters":{
      "url":{
         "function":"concat",
         "args":[
            "http://example.com",
            "/test?date=",
            { "function": "string_to_date",
                "args": [
                  "yesterday",
                  "%Y-%m-%d"
                ]
              }
         ]
      }
   }
}

```

#### string_to_date

Function converting string value into a datestring in specified format. The value may be either date in `YYYY-MM-DD` format,
or a relative period e.g. `5 hours ago`, `yesterday`,`3 days ago`, `4 months ago`, `2 years ago`, `today`.

The result is returned as a date string in the specified format, by default `%Y-%m-%d`

The function takes two arguments:

1. [REQ] Date string
2. [OPT] result date format. The format should be defined as in http://strftime.org/



**Example**

```json
{
   "user_parameters":{
      "yesterday_date":{
         "function":"string_to_date",
         "args":[
            "yesterday",
            "%Y-%m-%d"
         ]
      }
   }
}
```

The above value is then available in step contexts as:

```json
"to_date": {"attr": "yesterday_date"}
```

#### concat

Concat an array of strings.

The function takes an array of strings to concat as an argument



**Example**

```json
{
   "user_parameters":{
      "url":{
         "function":"concat",
         "args":[
            "http://example.com",
            "/test"
         ]
      }
   }
}
```

The above value is then available in step contexts as:

```json
"url": {"attr": "url"}
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

## Development

This example contains runnable container with simple unittest. For local testing it is useful to include `data` folder in the root
and use docker-compose commands to run the container or execute tests.

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path:
```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

Clone this repository, init the workspace and run the component with following command:

```
git clone https://bitbucket.org:kds_consulting_team/kds-team.ex-http-extended.git my-new-component
cd my-new-component
docker-compose build
docker-compose run --rm dev
```

Run the test suite and lint check using this command:

```
docker-compose run --rm test
```

# Integration

For information about deployment and integration with KBC, please refer to the [deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/)