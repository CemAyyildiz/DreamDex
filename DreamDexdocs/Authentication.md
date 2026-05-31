# Authentication

The DEX uses [Sign-In with Ethereum (ERC-4361)](https://eips.ethereum.org/EIPS/eip-4361) for authentication. Authentication is required for private endpoints such as [preparing orders](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/trading#post-v0-markets-symbol-orders) and [vault operations](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/vault); public [market data](https://docs.dreamdex.io/ld25g222WKDrLlJMcR41/developers/http-api/market-data) endpoints do not require it.

To authenticate, first request a nonce, include it in a SIWE message signed by your wallet, then submit the signed message to receive a JWT bearer token.

### Get authentication nonce

GET https://api.dreamdex.io

/v0/auth/nonce

Returns a cryptographically random nonce for use in Sign-In with Ethereum (ERC-4361) authentication. The nonce is single-use and expires after 5 minutes. Include this nonce in your SIWE message when authenticating.

Responses

200
Authentication nonce for SIWE

application/json

nonce string Required
Cryptographically random nonce for SIWE message

Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

```text
GET /v0/auth/nonce HTTP/1.1
Host: api.dreamdex.io
Accept: */*
```

```json
{
  "nonce": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

### Authenticate with SIWE

POST https://api.dreamdex.io

/v0/auth/login

Authenticates a user by verifying a signed ERC-4361 (Sign-In with Ethereum) message. The message must include a valid nonce obtained from the /auth/nonce endpoint. Returns a JWT bearer token for authenticating subsequent requests. The token should be included in the Authorization header as "Bearer ".

Body

application/json

message string Required
The ERC-4361 SIWE message that was signed

Example: `api.dreamdex.io wants you to sign in with your Ethereum account...`

signature string Required
The signature of the SIWE message (0x-prefixed hex)

Example: `0x1234567890abcdef...`

Pattern: `^0x[a-fA-F0-9]+$`

Responses

200
JWT bearer token for authenticated requests

application/json

expiresAt integer · int64 Required
Unix Timestamp (ms)

Example: `1765534169841`

token string Required
JWT bearer token to include in Authorization header

Example: `eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...`

400
Error response

application/json

401
Error response

application/json

```text
POST /v0/auth/login HTTP/1.1
Host: api.dreamdex.io
Content-Type: application/json
Accept: */*
Content-Length: 415

{
  "message": "api.dreamdex.io wants you to sign in with your Ethereum account:\n0x1234567890abcdef1234567890abcdef12345678\n\nSign in to dreamDEX\n\nURI: https://api.dreamdex.io\nVersion: 1\nChain ID: 50312\nNonce: a1b2c3d4e5f6g7h8\nIssued At: 2025-01-01T00:00:00.000Z",
  "signature": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1c"
}
```

```json
{
  "expiresAt": 1765537769841,
  "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Previous Error Handling
Next Market Data
Last updated 2 months ago