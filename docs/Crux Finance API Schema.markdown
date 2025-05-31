# Crux Finance API Schema

This document outlines the API endpoints for Crux Finance, categorized by their respective sections: `coingecko`, `crux`, `dex`, `spectrum`, and `trading_view`.

## coingecko

- **GET** `/coingecko/erg_history`  
  Retrieves historical data for Ergo (ERG) from CoinGecko.

- **GET** `/coingecko/erg_price`  
  Fetches the current price of Ergo (ERG) from CoinGecko.

## crux

- **GET** `/crux/asset_info/{token_id}`  
  Retrieves information about a specific asset identified by `token_id`.

- **POST** `/crux/asset_v2`  
  Submits data for an asset (version 2).

- **GET** `/crux/circulating_supply/{token_id}`  
  Fetches the circulating supply of a specific token identified by `token_id`.

- **GET** `/crux/explorer_tx_history`  
  Retrieves transaction history from the explorer.

- **GET** `/crux/gold_oracle_history`  
  Fetches historical data for the gold oracle.

- **GET** `/crux/info`  
  Retrieves general information about Crux Finance.

- **POST** `/crux/mainly_csv_extract`  
  Extracts data in CSV format (main extraction endpoint).

- **POST** `/crux/lp`  
  Submits data related to liquidity pools.

- **POST** `/crux/portfolio`  
  Submits portfolio-related data.

- **POST** `/crux/random_tx/{address}`  
  Submits a random transaction for a given `address`.

- **POST** `/crux/random_staked_positions`  
  Submits data for randomly staked positions.

- **GET** `/crux/token_info/{token_id}`  
  Retrieves information about a specific token identified by `token_id`.

- **POST** `/crux/tx_history`  
  Submits transaction history data.

- **POST** `/crux/tx_history_csv`  
  Submits transaction history data in CSV format.

- **GET** `/crux/tx_stats/{tx_id}`  
  Retrieves statistics for a specific transaction identified by `tx_id`.

- **POST** `/crux/vested_positions`  
  Submits data for vested positions.

## dex

- **GET** `/dex/order_history`  
  Fetches the order history for decentralized exchange (DEX) transactions.

- **GET** `/dex/order_history/ws`  
  Provides a WebSocket endpoint for real-time order history updates. The handles for the HTTP requests (this gets called when the HTTP GET lands at the start).

## spectrum

- **POST** `/spectrum/actions`  
  Submits actions to the Spectrum protocol.

- **GET** `/spectrum/price`  
  Retrieves the current price from the Spectrum protocol.

- **GET** `/spectrum/price_stats`  
  Fetches price statistics from the Spectrum protocol.

- **GET** `/spectrum/token_list`  
  Retrieves a list of tokens supported by the Spectrum protocol.

## trading_view

- **GET** `/trading_view/config`  
  Fetches the configuration for TradingView integration.

- **GET** `/trading_view/history`  
  Retrieves historical data for TradingView.

- **GET** `/trading_view/search`  
  Provides search functionality for TradingView.

- **GET** `/trading_view/symbols`  
  Fetches symbols supported by TradingView.

- **GET** `/trading_view/time`  
  Retrieves the current time for TradingView synchronization.