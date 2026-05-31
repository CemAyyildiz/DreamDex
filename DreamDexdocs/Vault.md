# Vault

The vault is an optional on-chain token custody mechanism. Orders [prepared via the HTTP API](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading#post-v0-markets-symbol-orders) default to `fundingSource: "wallet"`, which pulls tokens directly from the caller's wallet at execution time (requires an IOC or FOK order type and a prior ERC-20 approval to the SpotPool contract).

To use the vault instead, deposit tokens first and then set `fundingSource: "vault"` when [placing orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading#post-v0-markets-symbol-orders). The vault flow is:

1. Approve the pool contract to spend your tokens.
2. Deposit them into the vault.
3. [Place orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading#post-v0-markets-symbol-orders) funded from the vault balance.

Vault-funded orders support all order types including resting limit orders.

### Prepare ERC-20 approval

POST https://api.dreamdex.io

/v0/markets/{symbol}/vault/approve

Generates a standard ERC-20 `approve(spender, amount)` transaction that authorizes the pool contract to spend the given amount of a token on behalf of the wallet. The transaction targets the token contract (not the pool) because ERC-20 approve is called on the token itself.

This approval is required before:

- Vault deposits — the pool must be approved to transfer tokens into the vault via the deposit endpoint.
- Wallet-funded orders (`fundingSource: "wallet"`) — the pool must be approved to pull tokens for the atomic deposit-order-withdraw flow. The order response includes an `approval` field with the exact token and fee-inclusive amount needed.

For buy orders, approve the quote token (you spend quote to buy base). For sell orders, approve the base token. The amount must cover the order cost plus taker fee overhead from ceiling rounding.

Native token: when the currency is the chain's native token there is no ERC-20 to approve — deposits use the payable `depositNative()` entry point. In that case the endpoint responds with HTTP 200 and a body of JSON `null`, signaling the client to skip signing and proceed directly to the deposit endpoint.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Body

application/json

Parameters for a vault deposit, withdrawal, or approval transaction

amount string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`
Pattern: `^[0-9]+(\.[0-9]+)?$`

currency string Required
Currency code (e.g., "SOM" or "USD")

Example: `SOM`

walletAddress string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

Responses

200
EVM transaction payload the client MUST sign and send from their wallet, OR JSON `null` if no transaction is required for this request. Used by vault/approve on native-token currencies: ERC-20 approve has no equivalent for the chain's native token, so the API responds with `null` and clients should skip signing and proceed directly to the deposit endpoint.

application/json

Unsigned EVM transaction payload for the client to sign and broadcast. For vault/approve on the native token, the API returns JSON `null` instead of this object — see the OrderTransactionOrNull response.

approval object Optional
ERC-20 pre-approval needed for a wallet-funded order. Only present when the caller's current on-chain allowance is insufficient for the order. When present, the client MUST submit token.approve(spotPoolAddress, amount) before broadcasting the order transaction. The amount includes the taker fee so the on-chain transferFrom never reverts due to insufficient allowance. When absent, the existing allowance already covers the order.

chainId string Required
EVM chain ID, as a decimal string

Example: `1`

data string Required
Hex-encoded data (0x-prefixed)

Example: `0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]*$`

gasLimit string Optional
Recommended gas limit, as a decimal string

Example: `250000`

nonce string Optional
A once-only value

Example: `abc123`

to string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

value string Required
Wei value to send, as a decimal string. Non-zero for payable calls such as vault `depositNative()` when depositing the chain's native token; zero for ERC-20 deposits and withdrawals.

Example: `0`

400
Error response

application/json

```text
POST /v0/markets/{symbol}/vault/approve HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Content-Type: application/json
Accept: */*
Content-Length: 96

{
  "amount": "100.5",
  "currency": "SOM",
  "walletAddress": "0xaAaAaAaAaAbBbBbBbBbBcCcCcCcCcCdDdDdDdDdD"
}
```

```json
{
  "approval": {
    "amount": "100.1",
    "token": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "chainId": "1",
  "data": "0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678",
  "gasLimit": "250000",
  "nonce": "abc123",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "value": "0"
}
```

### Prepare vault deposit

POST https://api.dreamdex.io

/v0/markets/{symbol}/vault/deposit

Generates an unsigned EVM transaction for depositing tokens into the market's vault. The caller must first approve the pool contract to spend the token via the approve endpoint. The response contains the transaction payload (to, data, value, chainId) that must be signed and broadcast by the client's wallet.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Body

application/json

Parameters for a vault deposit, withdrawal, or approval transaction

amount string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`
Pattern: `^[0-9]+(\.[0-9]+)?$`

currency string Required
Currency code (e.g., "SOM" or "USD")

Example: `SOM`

walletAddress string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

Responses

200
EVM transaction payload the client MUST sign and send from their wallet

application/json

Unsigned EVM transaction payload for the client to sign and broadcast. For vault/approve on the native token, the API returns JSON `null` instead of this object — see the OrderTransactionOrNull response.

approval object Optional
ERC-20 pre-approval needed for a wallet-funded order. Only present when the caller's current on-chain allowance is insufficient for the order. When present, the client MUST submit token.approve(spotPoolAddress, amount) before broadcasting the order transaction. The amount includes the taker fee so the on-chain transferFrom never reverts due to insufficient allowance. When absent, the existing allowance already covers the order.

chainId string Required
EVM chain ID, as a decimal string

Example: `1`

data string Required
Hex-encoded data (0x-prefixed)

Example: `0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]*$`

gasLimit string Optional
Recommended gas limit, as a decimal string

Example: `250000`

nonce string Optional
A once-only value

Example: `abc123`

to string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

value string Required
Wei value to send, as a decimal string. Non-zero for payable calls such as vault `depositNative()` when depositing the chain's native token; zero for ERC-20 deposits and withdrawals.

Example: `0`

400
Error response

application/json

```text
POST /v0/markets/{symbol}/vault/deposit HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Content-Type: application/json
Accept: */*
Content-Length: 96

{
  "amount": "100.5",
  "currency": "SOM",
  "walletAddress": "0xaAaAaAaAaAbBbBbBbBbBcCcCcCcCcCdDdDdDdDdD"
}
```

```json
{
  "approval": {
    "amount": "100.1",
    "token": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "chainId": "1",
  "data": "0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678",
  "gasLimit": "250000",
  "nonce": "abc123",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "value": "0"
}
```

### Prepare vault withdrawal

POST https://api.dreamdex.io

/v0/markets/{symbol}/vault/withdraw

Generates an unsigned EVM transaction for withdrawing tokens from the market's vault back to the caller's wallet. The response contains the transaction payload (to, data, value, chainId) that must be signed and broadcast by the client's wallet.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Body

application/json

Parameters for a vault deposit, withdrawal, or approval transaction

amount string Required
Quantity as decimal string for precision (e.g., "100.5")

Example: `100.1`
Pattern: `^[0-9]+(\.[0-9]+)?$`

currency string Required
Currency code (e.g., "SOM" or "USD")

Example: `SOM`

walletAddress string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

Responses

200
EVM transaction payload the client MUST sign and send from their wallet

application/json

Unsigned EVM transaction payload for the client to sign and broadcast. For vault/approve on the native token, the API returns JSON `null` instead of this object — see the OrderTransactionOrNull response.

approval object Optional
ERC-20 pre-approval needed for a wallet-funded order. Only present when the caller's current on-chain allowance is insufficient for the order. When present, the client MUST submit token.approve(spotPoolAddress, amount) before broadcasting the order transaction. The amount includes the taker fee so the on-chain transferFrom never reverts due to insufficient allowance. When absent, the existing allowance already covers the order.

chainId string Required
EVM chain ID, as a decimal string

Example: `1`

data string Required
Hex-encoded data (0x-prefixed)

Example: `0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]*$`

gasLimit string Optional
Recommended gas limit, as a decimal string

Example: `250000`

nonce string Optional
A once-only value

Example: `abc123`

to string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

value string Required
Wei value to send, as a decimal string. Non-zero for payable calls such as vault `depositNative()` when depositing the chain's native token; zero for ERC-20 deposits and withdrawals.

Example: `0`

400
Error response

application/json

```text
POST /v0/markets/{symbol}/vault/withdraw HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Content-Type: application/json
Accept: */*
Content-Length: 96

{
  "amount": "100.5",
  "currency": "SOM",
  "walletAddress": "0xaAaAaAaAaAbBbBbBbBbBcCcCcCcCcCdDdDdDdDdD"
}
```

```json
{
  "approval": {
    "amount": "100.1",
    "token": "0x1234567890abcdef1234567890abcdef12345678"
  },
  "chainId": "1",
  "data": "0xa9059cbb0000000000000000000000001234567890abcdef1234567890abcdef12345678",
  "gasLimit": "250000",
  "nonce": "abc123",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "value": "0"
}
```

### Get vault balances

GET https://api.dreamdex.io

/v0/markets/{symbol}/vault/balance

Returns the withdrawable balances for both the base and quote tokens in a market's vault for the specified wallet address. Use this to display available funds for trading or withdrawal.

Required scopes

This endpoint requires the following scopes:

- `account`

Authorizations

bearerAuth

Authorization string Required
Bearer auth

Path parameters

symbol string Required
Market symbol

Example: `SOM:USD`

Query parameters

walletAddress string Required
EVM-compatible address (0x-prefixed, checksummed)

Example: `0x1234567890abcdef1234567890abcdef12345678`
Pattern: `^0x[a-fA-F0-9]{40}$`

Responses

200
Withdrawable vault balances for a wallet

application/json

balances object[] Required
A single currency balance in the vault

400
Error response

application/json

```text
GET /v0/markets/{symbol}/vault/balance?walletAddress=0x1234567890abcdef1234567890abcdef12345678 HTTP/1.1
Host: api.dreamdex.io
Authorization: Bearer YOUR_SECRET_TOKEN
Accept: */*
```

```json
{
  "balances": [
    {
      "amount": "123.456",
      "currency": "SOM"
    },
    {
      "amount": "789.012",
      "currency": "USD"
    }
  ]
}
```

Previous Trading
Next Libraries
Last updated 2 months ago