# HTTP API

The HTTP API for Somnia DEX.

The DEX HTTP API provides a programmatic REST interface that allows integrators to list the currently-available markets and currencies, prepare orders for transmission, and receive real-time updates about all orders placed on Somnia.

See also the [WebSocket API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/websocket-api) for truly real-time communication with the DEX.

Note that, unlike some DEX services, the HTTP API is not sufficient to place an order - the client is expected to be able to connect to the Somnia network and transmit their order themselves. See the [POST /v0/markets/{symbol}/orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading#post-v0-markets-symbol-orders) method for more information.

Previous SpotRouter
Next Error Handling
Last updated 15 days ago