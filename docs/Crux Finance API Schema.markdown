Crux Finance API Endpoints
This document outlines the Crux Finance API endpoints, detailing the expected inputs (parameters and request bodies) and the response schemas for each endpoint. The information is derived from the provided Swagger UI documentation.
coingecko
GET /coingecko/erg_history
Description: Retrieves Ergo price history.
Parameters:

from (query, integer, int32): Start timestamp.
to (query, integer, int32): End timestamp.
countback (query, integer, int32, required): Number of data points to retrieve.
resolution (query, string, required): Data resolution (e.g., minute, hour).

Response (200, application/json):
[
  {
    "price": 0,
    "t": 0
  }
]

GET /coingecko/erg_price
Description: Retrieves current Ergo price.
Parameters: None.
Response (200, application/json):
{
  "price": 0,
  "t": 0
}

crux
GET /crux/asset_info/{token_id}
Description: Retrieves transactions in explorer format for a specific token.
Parameters:

token_id (path, string, required): Token ID.

Response (200, application/json):
["string"]

POST /crux/asset_info_v2
Description: Retrieves transactions in explorer format.
Parameters: None.
Request Body (application/json, required):
["string"]

Response (200, application/json):
["string"]

Note: Schema references to Octinal could not be resolved.
GET /crux/circulating_supply/{token_id}
Description: Retrieves token circulating supply.
Parameters:

token_id (path, string): Token ID.

Response (200, text/plain):
0

GET /crux/explorer_tx_history
Description: Retrieves transactions in explorer format.
Parameters:

from (query, integer, int64): Start timestamp.
to (query, integer, int64): End timestamp.
offset (query, integer, int32): Offset for pagination.
limit (query, integer, int32): Number of results to return.
address (query, string): Address filter.

Response (200, application/json):
["string"]

GET /crux/gold_oracle_history
Description: Retrieves gold oracle price history.
Parameters: None.
Response (200, application/json):
[
  {
    "erg_per_gold_1g": 0,
    "timestamp": 0,
    "usd_per_erg": 0
  }
]

GET /crux/info
Description: Retrieves status of Crux database.
Parameters: None.
Response (200, application/json):
{
  "duckpools_height": 0,
  "ergopad_height": 0,
  "s_reduced_height": 0,
  "spectrum_height": 0
}

POST /crux/koinly_csv_export
Description: Initiates extraction of Koinly CSV.
Parameters:

API-KEY (header, string, required): API key.

Request Body (application/json, required):
{
  "from_time": 0,
  "to_time": 0,
  "user": "string",
  "wallets": [
    {
      "addresses": [
        {"string"},
        {
          "name": "string"
        }
      ]
    }
  ]
}

Response (200, application/json):
{
  "job_id": "string",
  "message": "string"
}

POST /crux/lp
Description: Retrieves portfolio liquidity pool positions.
Parameters: None.
Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        },
        {
          "label": "string",
          "owned": true
        }
      ]
    }
  ]
}

Response (200, application/json):
[
  {
    "base_current_proceeds": 0,
    "base_current_price": {
      "erg": 0,
      "usd": 0
    },
    "base_provided_amount": 0,
    "base_token_id": "string",
    "base_token_name": "string",
    "quote_current_amount": 0,
    "quote_current_price": {
      "erg": 0,
      "usd": 0
    },
    "quote_provided_amount": 0,
    "quote_token_id": "string",
    "quote_token_name": "string"
  }
]

POST /crux/portfolio
Description: Retrieves portfolio content.
Parameters: None.
Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[
  {
    "decimals": 0,
    "amount": 0,
    "token_description": "string",
    "token_id": "string",
    "token_name": "string",
    "value_in_erg": 0,
    "wrapped_tokens": ["string"]
  }
]

POST /crux/positions
Description: Retrieves portfolio positions.
Parameters: None.
Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[
  {
    "cost_basis": {
      "usd": 0
    },
    "last_price": {
      "erg": 0,
      "usd": 0
    },
    "pnl_day": {
      "erg": 0,
      "usd": 0
    },
    "pnl_day_pct": {
      "erg": 0,
      "usd": 0
    },
    "pnl_open": {
      "erg": 0,
      "usd": 0
    },
    "pnl_open_pct": {
      "usd": 0
    },
    "pnl_year": {
      "erg": 0,
      "usd": 0
    }
  }
]

GET /crux/random_tx/{address}
Description: Retrieves a random unsigned transaction.
Parameters:

address (path, string, required): Ergo address.

Response (200, application/json):
"string"

POST /crux/staked_chronology
Description: Retrieves portfolio staked positions.
Parameters: None.
Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[
  {
    "current_price": {
      "erg": 0,
      "usd": 0
    },
    "reward_amount": 0,
    "staked_amount": 0,
    "token_id": "string",
    "token_name": "string",
    "unstaked_amount": 0
  }
]

GET /crux/token_info/{token_id}
Description: Retrieves token information.
Parameters:

token_id (path, string, required): Token ID.

Response (200, application/json):
{
  "burned_supply": 0,
  "decimals": 0,
  "liquid_supply": 0,
  "amount": 0,
  "token_description": "string",
  "token_id": "string",
  "token_name": "string",
  "value_in_erg": 0
}

POST /crux/tx_history
Description: Retrieves portfolio transaction history.
Parameters:

from (query, integer, int64): Start timestamp.
to (query, integer, int64): End timestamp.
offset (query, integer, int32): Offset for pagination.
limit (query, integer, int32): Number of results to return.

Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[
  {
    "chained_transaction_id": "string",
    "time": 0,
    "transaction_elements": [
      {
        "from_address": "string",
        "to_address": "string",
        "token_amount": 0,
        "token_decimals": 0,
        "token_id": "string",
        "token_name": "string",
        "token_value": {
          "erg": 0,
          "usd": 0
        }
      }
    ],
    "transaction_id": "string"
  }
]

POST /crux/tx_history/csv
Description: Retrieves portfolio transaction history in CSV format.
Parameters:

from (query, integer, int64): Start timestamp.
to (query, integer, int64): End timestamp.
offset (query, integer, int32): Offset for pagination.
limit (query, integer, int32): Number of results to return.

Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[]

GET /crux/tx_status/{tx_id}
Description: Retrieves transaction status.
Parameters:

tx_id (path, string, required): Transaction ID.

Response (200, application/json):
{
  "num_confirmations": 0
}

POST /crux/vested_positions
Description: Retrieves portfolio vested positions.
Parameters: None.
Request Body (application/json, required):
{
  "addresses": ["string"],
  "wallets": [
    {
      "addresses": [
        {
          "address": "string",
          "label": "string"
        }
      ],
      "label": "string",
      "owned": true
    }
  ]
}

Response (200, application/json):
[
  {
    "current_price": {
      "erg": 0,
      "usd": 0
    },
    "initial_vested_amount": 0,
    "remaining_amount": 0,
    "token_id": "string",
    "token_name": "string"
  }
]

dex
GET /dex/order_history
Description: Retrieves portfolio order history.
Parameters:

token_id (query, string): Token ID.
offset (query, integer, int32, required): Offset for pagination.
limit (query, integer, int32, required): Number of results to return.
min_id (query, integer, int64): Minimum order ID.
max_id (query, integer, int64): Maximum order ID.
addresses (query, string): Address filter.
order_types (query, string): Order type filter.

Response (200, application/json):
[
  {
    "base_name": "string",
    "chain_time": 0,
    "amount": 0,
    "filled_base_amount": "string",
    "filled_quote_amount": "string",
    "id": 0,
    "maker_address": "string",
    "order_base_amount": "string",
    "order_quote_amount": "string",
    "quote_amount": "string",
    "quote_name": "string",
    "status": "string",
    "taker_address": "string",
    "total_filled_base_amount": "string",
    "total_filled_quote_amount": "string",
    "transaction_id": "string"
  }
]

Note: Schema references to Decimal could not be resolved.
GET /dex/order_history/ws
Description: WebSocket handler for order history.
Parameters:

token_id (query, string): Token ID.
offset (query, integer, int32, required): Offset for pagination.
limit (query, integer, int32): Number of results to return.
min_id (query, integer, int64): Minimum order ID.
max_id (query, integer, int64): Maximum order ID.
addresses (query, string): Address filter.
order_types (query, string): Order type filter.

Response (200, application/json):
[
  {
    "base_name": "string",
    "chain_time": 0,
    "amount": 0,
    "filled_base_amount": "string",
    "filled_quote_amount": "string",
    "id": 0,
    "maker_address": "string",
    "order_base_amount": "string",
    "order_quote_amount": "string",
    "quote_amount": "string",
    "quote_name": "string",
    "status": "string",
    "taker_address": "string",
    "total_filled_base_amount": "string",
    "total_filled_quote_amount": "string",
    "transaction_id": "string"
  }
]

spectrum
POST /spectrum/actions
Description: Retrieves spectrum actions.
Parameters: None.
Request Body (application/json, required):
{
  "base_id": "string",
  "base_token": "string",
  "limit": 0,
  "amount": 0,
  "quote_id": "string",
  "quote_token": "string",
  "user_address": "string"
}

Response (200, application/json):
[
  {
    "action_amount": "string",
    "action_type": "string",
    "base_id": "string",
    "base_name": "string",
    "ergo_price": 0,
    "price_in_ergo": 0,
    "quote_id": "string",
    "quote_token": "string",
    "time": 0,
    "user_address": "string"
  }
]

GET /spectrum/price
Description: Retrieves price for a token.
Parameters:

token_id (query, string): Token ID.
time_point (query, integer, int64): Specific timestamp.

Response (200, application/json):
{
  "asset_price_erg": 0,
  "erg_price_usd": 0
}

GET /spectrum/price_stats
Description: Retrieves price statistics for a token.
Parameters:

token_id (query, string): Token ID.
time_point (query, integer, int64, required): Specific timestamp.
time_window (query, integer, int64, required): Time window for stats.

Response (200, application/json):
{
  "average": {
    "erg": 0,
    "usd": 0
  },
  "max": {
    "erg": 0,
    "usd": 0
  },
  "min": {
    "erg": 0,
    "usd": 0
  },
  "token_info": "string"
}

Note: Schema reference to BasicTokenInfo could not be resolved.
POST /spectrum/token_list
Description: Retrieves spectrum tokens.
Parameters: None.
Request Body (application/json, required):
{
  "buys_max": 0,
  "buys_min": 0,
  "filter_window": "Hour",
  "limit": 0,
  "liquidity_max": 0,
  "liquidity_min": 0,
  "market_cap_max": 0,
  "market_cap_min": 0,
  "name_filter": "string",
  "offset": 0,
  "pct_change_max": 0,
  "pct_change_min": 0,
  "price_max": 0,
  "price_min": 0,
  "sells_max": 0,
  "sells_min": 0,
  "sort_by": "Volume",
  "sort_order": "Asc",
  "token_filter": ["string"],
  "volume_max": 0,
  "volume_min": 0
}

Response (200, application/json):
[
  {
    "buys": 0,
    "created": 0,
    "day_change_erg": 0,
    "day_change_usd": 0,
    "erg_price_usd": 0,
    "exchanges": ["string"],
    "last_price_erg": 0,
    "last_price_usd": 0,
    "liquid_supply": 0,
    "liquidity": 0,
    "market_cap": 0,
    "sells": 0,
    "token_id": "string",
    "token_name": "string",
    "volume": 0
  }
]

trading_view
GET /trading_view/history
Description: Retrieves OHLCV history for a specified symbol.
Parameters:

symbol (query, string): Symbol identifier.
from (query, integer, int32, required): Start timestamp.
to (query, integer, int32, required): End timestamp.
resolution (query, string, required): Data resolution.
countback (query, integer, int32, required): Number of data points.

Response (200, application/json):
[
  {
    "c": [0],
    "errmsg": "string",
    "h": [0],
    "l": [0],
    "s": ["string"],
    "t": [0],
    "v": [0]
  }
]

GET /trading_view/search
Description: Searches for a symbol.
Parameters:

query (query, string): Search query.
type (query, string): Symbol type.
exchange (query, string): Exchange filter.
limit (query, integer, int32): Number of results.

Response (200, application/json):
[
  {
    "description": "string",
    "exchange": "string",
    "format": "string",
    "full_name": "string",
    "has_intraday": true,
    "intraday_multipliers": ["string"],
    "listed_exchange": "string",
    "minmov": 0,
    "name": "string",
    "pricescale": 0,
    "session": "string",
    "supported_resolutions": ["string"],
    "symbol": "string",
    "timezone": "string",
    "type": "string"
  }
]

GET /trading_view/symbols
Description: Retrieves symbol information.
Parameters:

symbol (query, string): Symbol identifier.

Response (200, application/json):
{
  "description": "string",
  "exchange": "string",
  "format": "string",
  "full_name": "string",
  "has_intraday": true,
  "intraday_multipliers": ["string"],
  "listed_exchange": "string",
  "minmov": 0,
  "name": "string",
  "pricescale": 0,
  "session": "string",
  "supported_resolutions": ["string"],
  "symbol": "string",
  "timezone": "string",
  "type": "string"
}

GET /trading_view/time
Description: Retrieves server time.
Parameters: None.
Response (200, text/plain):
string

Notes

Schema Errors: The original document contains unresolved schema references (e.g., BasicTokenInfo, Decimal, Octinal). These fields are likely intended to be numeric or structured data but could not be fully specified.
Typographical Errors: The OCR output includes typos (e.g., "scheea" instead of "schema", "fref" instead of "$ref"). These have been corrected where possible in the Markdown.
API Base URL: All endpoints are relative to https://api.cruxfinance.io.

This Markdown provides a clear and structured overview of the Crux Finance API endpoints for reference and implementation.
