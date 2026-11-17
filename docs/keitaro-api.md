# Keitaro Admin API reference

The subset of the Keitaro Admin API v1 this project uses. Taken from the instance's Swagger spec (`https://tlgk.host/admin/?object=adminApi`, needs admin login) and real responses from the instance.

## Basics
- Base URL: `https://tlgk.host/admin_api/v1`
- Auth: header `Api-Key: <KEITARO_API_KEY>`. A missing or invalid key returns `401`
- JSON in and out
- Timestamps are `YYYY-MM-DD HH:MM:SS` strings without a timezone
- This is a **shared test instance**: other people's campaigns, groups and offers live here too. Never modify or delete anything this app did not create

## Instance defaults
| Entity | id | Name |
|---|---|---|
| Domain | `1813` | `kylovoa.com` (the only domain) |
| Campaign group | `10332` | `FORTESTS` |
| Traffic source | `836` | `FORTESTS` (the only source) |

## Endpoints used

### Reference data
| Method | Path | Notes |
|---|---|---|
| GET | `/domains` | `[{id, name, is_ssl, state, ...}]` |
| GET | `/groups?type=campaigns` | `[{id, name, position, type}]` |
| GET | `/traffic_sources` | `[{id, name, state, ...}]` |
| GET | `/offers` | All offers, **no search or pagination params**. ~170 items |

Offer shape (relevant fields):
```json
{ "id": 25327, "name": "25327 Flexacil [JOINT-PE-JO_0062] ...", "group": "JO Flexacil PE",
  "country": ["Peru"], "state": "active" }
```

### Campaigns
| Method | Path | Notes |
|---|---|---|
| GET | `/campaigns?offset=&limit=` | List campaigns |
| GET | `/campaigns/{id}` | One campaign |
| POST | `/campaigns` | Create |
| PUT | `/campaigns/{id}` | Update, partial body |
| DELETE | `/campaigns/{id}` | Moves campaign to archive |
| GET | `/campaigns/{id}/streams` | Campaign streams ("flows"), with filters and offers inline |

`POST /campaigns` body (`*` = required):
```
alias*              string   used in the URL: https://domain/ALIAS
name*               string
type                position | weight   (stream rotation, default position)
domain_id           integer
group_id            string   (spec says string even though it is an id)
traffic_source_id   integer
state               active | disabled
cost_type           CPC | CPUC | CPM
cost_value, cost_currency, cost_auto, cookies_ttl, notes, token, parameters, postbacks
```
Campaign response (relevant fields):
```json
{ "id": 212636, "alias": "zz-lyudvig-smoke2-6692dded", "name": "zz_lyudvig_smoke2", "type": "position",
  "state": "active", "domain_id": 1813, "domain": "https://kylovoa.com/",
  "group_id": 10332, "group": "FORTESTS", "traffic_source_id": 836 }
```
Campaign tracking URL = `{domain}{alias}`.

### Streams (flows)
| Method | Path | Notes |
|---|---|---|
| POST | `/streams` | Create a stream in a campaign |
| GET | `/streams/{id}` | One stream |
| PUT | `/streams/{id}` | Update, partial body |
| DELETE | `/streams/{id}` | Moves stream to archive |

`POST /streams` body (`*` = required):
```
campaign_id*     integer
type*            regular | default | forced
name*            string
schema*          redirect | landings | action
action_type*     string   e.g. "http" (302 redirect)
action_payload   string   redirect URL when schema = redirect
position         integer
state            active | disabled
filters          [{ name*, mode*: accept | reject, payload: [string] }]
offers           [{ offer_id*, share*: integer, state: active | disabled }]
collect_clicks, filter_or, weight, comments, triggers, landings
```
`PUT /streams/{id}` takes the same fields, none required.

Reference values:
- `/stream_types`: `regular`, `default`, `forced`
- `/stream_schemas`: `landings` (landing pages & offers), `redirect` (direct URL), `action`
- `/streams_actions`: `http` is the recommended 302 redirect

## Recipes

### Create a campaign (part 1)
1. `POST /campaigns` with `{alias, name, type: "position", domain_id, group_id, traffic_source_id}`
2. `POST /streams` for the geo stream:
   ```json
   { "campaign_id": 1, "type": "regular", "name": "Geo → Google", "position": 1,
     "schema": "redirect", "action_type": "http", "action_payload": "https://google.com",
     "filters": [{ "name": "country", "mode": "accept", "payload": ["AU"] }] }
   ```
3. `POST /streams` for the offer stream:
   ```json
   { "campaign_id": 1, "type": "default", "name": "Offers", "position": 2,
     "schema": "landings", "action_type": "http",
     "offers": [{ "offer_id": 13972, "share": 100, "state": "active" }] }
   ```
4. If step 2 or 3 fails, `DELETE /campaigns/{id}` to avoid leaving a half-built campaign

Real example of the result (`GET /campaigns/212636/streams`, another user's campaign):
```json
[
  { "id": 1313833, "type": "regular", "name": "Country AU → Google", "position": 1,
    "schema": "redirect", "action_type": "http", "action_payload": "https://www.google.com/",
    "filters": [{ "id": 2965598, "name": "country", "mode": "accept", "payload": ["AU"] }],
    "offers": [] },
  { "id": 1313834, "type": "default", "name": "Offer", "position": 2,
    "schema": "landings", "action_type": "http", "action_payload": "",
    "filters": [],
    "offers": [{ "id": 2063610, "stream_id": 1313834, "offer_id": 13972, "share": 100, "state": "active" }] }
]
```

### Edit offers in a campaign (part 2)
- **Read**: `GET /campaigns/{id}/streams`, take the stream with `schema = "landings"` (the `default` one)
- **Push**: `PUT /streams/{stream_id}` with the full desired `offers` list: `[{offer_id, share, state: "active"}]`
- **Remove an offer**: push the list without it. Never call `/offers/{id}/archive`, which archives the offer itself for every campaign

## Admin UI links
- Campaign editor: `{KEITARO_BASE_URL}/admin/#!/campaign/{id}/main` (verified)

## Data quirks seen on the instance
- `offer.country` is usually a list of country names, but can be an empty string `""`
- `campaign.domain` and `campaign.domain_id` are `null` for campaigns without a domain
- `GET /campaigns/{id}` for a missing id returns `404` with a plain-text body

## Implications for our implementation
- **Offer search**: the API has no search, so the backend caches `GET /offers` briefly and filters by id or name substring itself
- **Shares** are integers. They should sum to 100 for the stream
- **Alias** is required and must be unique: generate it from a name slug plus a short random suffix
- **Geo filter** payload uses ISO alpha-2 codes (`"AU"`), even though the UI shows country names
- **Group id** is sent as a string in campaign bodies but returned as an integer

## Behaviour we rely on
- `PUT /streams/{id}` with `offers` replaces the whole list: an offer left out is removed from the stream. Deleting from the editor depends on this and was checked manually
- We always send shares that sum to exactly 100, so whether Keitaro would normalize other totals does not matter to us
- Error bodies are not consistent (`404` is plain text), so the client never parses them: it maps the status code to a `ProviderError` or `NotFoundError` and logs the first 500 characters of the body
