# OpenAPI

OpenAPI documentation: <https://api.pms.ema.europa.eu/public/v1/swagger>.

Endpoints:

* Find a medicinal product
* Get all details of a medicinal product

The response contains coded elements with codes from RMS, without display names.

Get a token with `curl`:

```bash
curl --fail-with-body --silent --show-error \
  --user "$PMS_CLIENT_ID:$PMS_CLIENT_SECRET" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=client_credentials' \
  --data-urlencode "scope=$PMS_SCOPE" \
  "$PMS_TOKEN_URL"
```

# Terminology

* Lists and terms are from RMS: <https://spor.ema.europa.eu/rmswi/#/>.
* The lists can be downloaded in several formats, including XML.
  * Lists needed by the application can be downloaded and pre-processed.
* The RMS API requires registration.
  * In v1 the username and password is shared with the user's EMA ID.

Example:

```
GET https://spor-uat.ema.europa.eu/v1/lists/200000000004/terms/100000073788
Authorization: Basic
```

# Examples

## Estonia

Get the national package database XML: <https://www.ravimiregister.ee/en/publichomepage.aspx?pv=PublicDownloads>.

* Find products by properties of the package, e.g. MA-number.
* Get the MedicinalProductDefinition PMS ID from the response.
* Get all details (including packages and marketing authorization information) from the `$everything endpoint`.

Development suggestions:

* Can the national database expose data in a similar structure?
* Can the PMS FHIR format be used to add data to the database?
