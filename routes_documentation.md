# Finance Hack API Routes Documentation

## Example User Data Model

Below is an example of a complete user profile with their financial data:

```json
{
  "user": {
    "id": 123,
    "name": "Sarah Johnson",
    "email": "sarah.johnson@example.com",
    "created_at": "2023-01-15T08:30:00Z"
  },
  "financial_summary": {
    "id": 456,
    "user_id": 123,
    "savings_balance": 15750.25,
    "investment_balance": 42000.00,
    "debt_balance": 8500.00,
    "income_id" : 789,
    "expense_id" : 101,
    "last_updated": "2023-06-01T12:00:00Z"
  },
  "income": {
    "id": 789,
    "financial_summary_id": 456,
    "salary": 5800.00,
    "investments": 350.00,
    "business_income": 1200.00,
    "month": "June 2023"
  },
  "expenses": {
    "id": 101,
    "financial_summary_id": 456,
    "rent_mortgage": 1650.00,
    "utilities": 215.50,
    "insurance": 180.00,
    "loan_payments": 350.00,
    "groceries": 480.00,
    "transportation": 175.00,
    "subscriptions": 65.00,
    "entertainment": 220.00,
    "month": "June 2023"
  },
  "buckets": [
    {
      "id": 201,
      "user_id": 123,
      "name": "Emergency Fund",
      "target_amount": 10000.00,
      "current_saved_amount": 8500.00,
      "priority_score": 5,
      "deadline": null,
      "status": "active"
    },
    {
      "id": 202,
      "user_id": 123,
      "name": "Europe Vacation",
      "target_amount": 5000.00,
      "current_saved_amount": 2800.00,
      "priority_score": 3,
      "deadline": "2023-12-15T00:00:00Z",
      "status": "active"
    },
    {
      "id": 203,
      "user_id": 123,
      "name": "New Car Down Payment",
      "target_amount": 8000.00,
      "current_saved_amount": 4450.00,
      "priority_score": 4,
      "deadline": "2024-03-01T00:00:00Z",
      "status": "active"
    }
  ],
  "recent_transactions": [
    {
      "id": 301,
      "user_id": 123,
      "amount": -85.43,
      "description": "Grocery Store Purchase",
      "category": "Food",
      "transaction_date": "2023-06-01T14:30:00Z",
      "reference": "T78945612",
      "is_reconciled": true
    },
    {
      "id": 302,
      "user_id": 123,
      "amount": -120.00,
      "description": "Electricity Bill",
      "category": "Utilities",
      "transaction_date": "2023-05-28T09:15:00Z",
      "reference": "T78945589",
      "is_reconciled": true
    },
    {
      "id": 303,
      "user_id": 123,
      "amount": 5800.00,
      "description": "Monthly Salary",
      "category": "Income",
      "transaction_date": "2023-05-25T08:00:00Z",
      "reference": "T78945501",
      "is_reconciled": true
    },
    {
      "id": 304,
      "user_id": 123,
      "amount": -250.00,
      "description": "Transfer to Europe Vacation Bucket",
      "category": "Savings",
      "transaction_date": "2023-05-25T10:30:00Z",
      "reference": "T78945510",
      "is_reconciled": true
    }
  ]
}
```

## Workflow Explanation

This section explains the end-to-end workflow represented in these API routes:

### Authentication Flow
1. **User Registration**: A new user starts by registering through the `/users/` endpoint.
   - This creates a user account with name, email, and password.
2. **Authentication**: Users authenticate through the OAuth 2.0 flow:
   - First, request an authorization code at `/auth/authorize`
   - Then, exchange the code for a token at `/auth/token`

### User Management
3. **User Operations**: 
   - Create users: `POST /users/`
   - View user details: `GET /users/{user_id}`
   - Update user information: `PUT /users/{user_id}`
   - Delete users: `DELETE /users/{user_id}`

### Financial Management

#### Transactions
4. **Transaction Tracking**:
   - Create transactions: `POST /transactions/`
   - View transaction details: `GET /transactions/{transaction_id}`
   - Update transactions: `PUT /transactions/{transaction_id}`
   - Delete transactions: `DELETE /transactions/{transaction_id}`

#### Financial Summary
5. **Financial Summary Management**:
   - Create summaries: `POST /financial-summaries/`
   - View summary details: `GET /financial-summaries/{financial_summary_id}`
   - Update summaries: `PUT /financial-summaries/{financial_summary_id}`
   - Delete summaries: `DELETE /financial-summaries/{financial_summary_id}`

#### Income Tracking
6. **Income Management**:
   - Create income records: `POST /incomes/`
   - View income details: `GET /incomes/{income_id}`
   - Update income records: `PUT /incomes/{income_id}`
   - Delete income records: `DELETE /incomes/{income_id}`

#### Expenses Tracking
7. **Expenses Management**:
   - Create expense records: `POST /expenses/`
   - View expense details: `GET /expenses/{expenses_id}`
   - Update expense records: `PUT /expenses/{expenses_id}`
   - Delete expense records: `DELETE /expenses/{expenses_id}`

#### Savings Buckets
8. **Savings Bucket Management**:
   - Create savings buckets: `POST /buckets/`
   - View bucket details: `GET /buckets/{bucket_id}`
   - Update buckets: `PUT /buckets/{bucket_id}`
   - Delete buckets: `DELETE /buckets/{bucket_id}`

## API Routes Reference

### Authentication Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/auth/authorize` | POST | Request authorization code | `{ client_id, redirect_uri, code_challenge }` | `{ auth_code }` |
| `/auth/token` | POST | Exchange code for token | `{ grant_type, code, code_verifier }` | `{ access_token, token_type }` |

#### Example: Request Authorization Code

Request:
```json
{
  "client_id": "frontend-app",
  "redirect_uri": "http://localhost:3000/callback",
  "code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
}
```

Response:
```json
{
  "auth_code": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}
```

#### Example: Exchange Code for Token

Request:
```json
{
  "grant_type": "authorization_code",
  "code": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/users/` | POST | Create a new user | `{ name, email, password }` | User object |
| `/users/{user_id}` | GET | Get user details | Path parameter: user_id | User object |
| `/users/{user_id}` | PUT | Update user | Path parameter: user_id, Body: user data | Updated user object |
| `/users/{user_id}` | DELETE | Delete user | Path parameter: user_id | Deleted user object |

#### Example: Create User

Request:
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

Response:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

#### Example: Get User

Response:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

#### Example: Update User

Request:
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

Response:
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

#### Example: Delete User

Response:
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

### Transaction Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/transactions/` | POST | Create a transaction | Transaction data | Created transaction |
| `/transactions/{transaction_id}` | GET | Get transaction details | Path parameter: transaction_id | Transaction object |
| `/transactions/{transaction_id}` | PUT | Update a transaction | Path parameter: transaction_id, Body: transaction data | Updated transaction |
| `/transactions/{transaction_id}` | DELETE | Delete a transaction | Path parameter: transaction_id | Deleted transaction |

#### Example: Create Transaction

Request:
```json
{
  "user_id": 1,
  "amount": 50.75,
  "description": "Grocery Shopping",
  "category": "Food",
  "transaction_date": "2023-03-20T15:30:00Z",
  "reference": "T123456",
  "notes": "Weekly shopping at Walmart",
  "is_reconciled": false
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 50.75,
  "description": "Grocery Shopping",
  "category": "Food",
  "transaction_date": "2023-03-20T15:30:00Z",
  "reference": "T123456",
  "notes": "Weekly shopping at Walmart",
  "is_reconciled": false
}
```

#### Example: Update Transaction

Request:
```json
{
  "amount": 52.99,
  "is_reconciled": true
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 52.99,
  "description": "Grocery Shopping",
  "category": "Food",
  "transaction_date": "2023-03-20T15:30:00Z",
  "reference": "T123456",
  "notes": "Weekly shopping at Walmart",
  "is_reconciled": true
}
```

### Financial Summary Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/financial-summaries/` | POST | Create a financial summary | Summary data | Created summary |
| `/financial-summaries/{financial_summary_id}` | GET | Get summary details | Path parameter: financial_summary_id | Summary object |
| `/financial-summaries/{financial_summary_id}` | PUT | Update a summary | Path parameter: financial_summary_id, Body: summary data | Updated summary |
| `/financial-summaries/{financial_summary_id}` | DELETE | Delete a summary | Path parameter: financial_summary_id | Deleted summary |

#### Example: Create Financial Summary

Request:
```json
{
  "user_id": 1,
  "savings_balance": 5000.00,
  "investment_balance": 10000.00,
  "debt_balance": 2000.00
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "savings_balance": 5000.00,
  "investment_balance": 10000.00,
  "debt_balance": 2000.00
}
```

#### Example: Update Financial Summary

Request:
```json
{
  "savings_balance": 5500.00,
  "debt_balance": 1800.00
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "savings_balance": 5500.00,
  "investment_balance": 10000.00,
  "debt_balance": 1800.00
}
```

### Income Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/incomes/` | POST | Create an income record | Income data | Created income record |
| `/incomes/{income_id}` | GET | Get income details | Path parameter: income_id | Income object |
| `/incomes/{income_id}` | PUT | Update an income record | Path parameter: income_id, Body: income data | Updated income record |
| `/incomes/{income_id}` | DELETE | Delete an income record | Path parameter: income_id | Deleted income record |

#### Example: Create Income

Request:
```json
{
  "financial_summary_id": 1,
  "salary": 5000.00,
  "investments": 250.00,
  "business_income": 1000.00
}
```

Response:
```json
{
  "id": 1,
  "financial_summary_id": 1,
  "salary": 5000.00,
  "investments": 250.00,
  "business_income": 1000.00
}
```

#### Example: Update Income

Request:
```json
{
  "salary": 5200.00,
  "investments": 300.00
}
```

Response:
```json
{
  "id": 1,
  "financial_summary_id": 1,
  "salary": 5200.00,
  "investments": 300.00,
  "business_income": 1000.00
}
```

### Expenses Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/expenses/` | POST | Create an expenses record | Expenses data | Created expenses record |
| `/expenses/{expenses_id}` | GET | Get expenses details | Path parameter: expenses_id | Expenses object |
| `/expenses/{expenses_id}` | PUT | Update an expenses record | Path parameter: expenses_id, Body: expenses data | Updated expenses record |
| `/expenses/{expenses_id}` | DELETE | Delete an expenses record | Path parameter: expenses_id | Deleted expenses record |

#### Example: Create Expenses

Request:
```json
{
  "financial_summary_id": 1,
  "rent_mortgage": 1500.00,
  "utilities": 200.00,
  "insurance": 150.00,
  "loan_payments": 300.00,
  "groceries": 400.00,
  "transportation": 150.00,
  "subscriptions": 50.00,
  "entertainment": 200.00
}
```

Response:
```json
{
  "id": 1,
  "financial_summary_id": 1,
  "rent_mortgage": 1500.00,
  "utilities": 200.00,
  "insurance": 150.00,
  "loan_payments": 300.00,
  "groceries": 400.00,
  "transportation": 150.00,
  "subscriptions": 50.00,
  "entertainment": 200.00
}
```

#### Example: Update Expenses

Request:
```json
{
  "groceries": 450.00,
  "subscriptions": 65.00
}
```

Response:
```json
{
  "id": 1,
  "financial_summary_id": 1,
  "rent_mortgage": 1500.00,
  "utilities": 200.00,
  "insurance": 150.00,
  "loan_payments": 300.00,
  "groceries": 450.00,
  "transportation": 150.00,
  "subscriptions": 65.00,
  "entertainment": 200.00
}
```

### Bucket Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/buckets/` | POST | Create a savings bucket | Bucket data | Created bucket |
| `/buckets/{bucket_id}` | GET | Get bucket details | Path parameter: bucket_id | Bucket object |
| `/buckets/{bucket_id}` | PUT | Update a bucket | Path parameter: bucket_id, Body: bucket data | Updated bucket |
| `/buckets/{bucket_id}` | DELETE | Delete a bucket | Path parameter: bucket_id | Deleted bucket |

#### Example: Create Bucket

Request:
```json
{
  "user_id": 1,
  "name": "Vacation Fund",
  "target_amount": 2000.00,
  "current_saved_amount": 500.00,
  "priority_score": 2,
  "deadline": "2023-12-31T00:00:00Z",
  "status": "active"
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Vacation Fund",
  "target_amount": 2000.00,
  "current_saved_amount": 500.00,
  "priority_score": 2,
  "deadline": "2023-12-31T00:00:00Z",
  "status": "active"
}
```

#### Example: Update Bucket

Request:
```json
{
  "current_saved_amount": 750.00,
  "priority_score": 3
}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Vacation Fund",
  "target_amount": 2000.00,
  "current_saved_amount": 750.00,
  "priority_score": 3,
  "deadline": "2023-12-31T00:00:00Z",
  "status": "active"
}
```

## Typical User Journey

1. User registers by creating an account
2. User authenticates using the OAuth flow to get an access token
3. User creates a financial summary for tracking their finances
4. User records income sources and regular expenses
5. User tracks individual transactions as they occur
6. User creates savings buckets for specific financial goals
7. User manages their financial data by updating or deleting records as needed
