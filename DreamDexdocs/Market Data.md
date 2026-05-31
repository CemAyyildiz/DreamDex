# Market Data

These public endpoints return information about available trading pairs, supported currencies, and current order book depth. No [authentication](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/authentication) is required.

### List markets

GET https://api.dreamdex.io

/v0/markets

Returns all trading pairs (markets) available on this exchange. Each market includes its symbol identifier along with base and quote currency information. Use this endpoint to discover tradeable pairs and to populate market selection interfaces. Markets are identified by symbols in the format "BASE:QUOTE" (e.g., "SOM:USD").

Responses

200
List of markets

application/json

markets object[] Required
Market information

```text
GET /v0/markets HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "markets": [
    {
      "base": "0xC732f848Ca9146840903cf5CC20481C4c56e0A11",
      "baseDecimals": 18,
      "contract": "0x9876543210abcdef9876543210abcdef98765432",
      "lotSize": "0.000001",
      "minQuantity": "0.001",
      "quote": "0x1e128F195b081Aa75CE1898227993D0994bf51e1",
      "quoteDecimals": 6,
      "symbol": "SOMI:USDC",
      "tickSize": "0.00001"
    }
  ]
}
```

### List currencies

GET https://api.dreamdex.io

/v0/currencies

Returns all currencies (tokens and assets) supported by this exchange. Each currency includes its identifier, ticker code, and display name. Use this endpoint to discover which assets are available for trading and to populate currency selection interfaces.

Responses

200
List of currencies

application/json

currencies object[] Required
Currency information

```text
GET /v0/currencies HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "currencies": [
    {
      "code": "SOMI",
      "decimals": 18,
      "id": "0xC732f848Ca9146840903cf5CC20481C4c56e0A11",
      "name": "Somnia"
    },
    {
      "code": "USDC",
      "decimals": 6,
      "id": "0x1e128F195b081Aa75CE1898227993D0994bf51e1",
      "name": "USD Coin"
    }
  ]
}
```

### Get order books

GET https://api.dreamdex.io

/v0/orderbooks

Returns aggregated order book data for one or more market symbols. The response includes all open bids and asks sorted by price, with quantities at each price level. Use the optional depth parameter to limit the number of price levels returned. Order books are essential for displaying market depth charts and calculating slippage estimates.

Query parameters

symbols string[] Required
Symbols of the order book to list

Example: `["SOM:USD","SOM:GBP"]`

depth integer Optional
Number of orders to return

Responses

200
List of order books

application/json

orderbooks object[] Required
Order book

Example: `{"asks":[],"bids":[],"symbol":"SOM:USD","timestamp":0}`

500
Error response

application/json

```text
GET /v0/orderbooks?symbols=SOM%3AUSD HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "orderbooks": [
    {
      "asks": [
        {
          "price": "1.26",
          "quantity": "800"
        },
        {
          "price": "1.27",
          "quantity": "2100"
        }
      ],
      "bids": [
        {
          "price": "1.24",
          "quantity": "1500"
        },
        {
          "price": "1.23",
          "quantity": "3200"
        }
      ],
      "nonce": "abc123",
      "symbol": "SOM:USD",
      "timestamp": 1765534169841
    }
  ]
}
```

Previous Authentication
Next Trading
Last updated 2 months ago