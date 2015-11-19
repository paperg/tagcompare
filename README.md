[![Code Climate](https://codeclimate.com/github/d3ming/tagcompare/badges/gpa.svg)](https://codeclimate.com/github/d3ming/tagcompare)
[![Test Coverage](https://codeclimate.com/github/d3ming/tagcompare/badges/coverage.svg)](https://codeclimate.com/github/d3ming/tagcompare/coverage)
[![Issue Count](https://codeclimate.com/github/d3ming/tagcompare/badges/issue_count.svg)](https://codeclimate.com/github/d3ming/tagcompare)

# TAGCOMPARE

## Setup
`make install` to install dependencies

### config.json
Make a local copy of [`config.json`](tagcompare/config.json) called `config.local.json`
Update the values for webdriver user/key and placelocal secret:
```json
  "webdriver": {
    "user": "USER",
    "key": "KEY"
  },
  "placelocal": {
    "domain": "www.placelocaldemo.com",
    "secret": {
      "pl-secret": "SECRET",
      "pl-service-identifier": "SERVICEID"
    }
  }
```

## Running the tool
`make run` will run the tool to capture screenshots and compare them

## Running tests
`make test` will run unit tests
