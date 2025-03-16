# Finance Hack API Routes Documentation

## Workflow Explanation

This section explains the end-to-end workflow represented in these API routes:

### Authentication Flow
1. **User Registration**: A new user starts by registering with their email, password, and name through the `/api/auth/signup` endpoint.
   - This creates a user account and returns an authentication token for immediate use.
2. **User Login**: Returning users authenticate through the `/api/auth/login` endpoint using their email and password.
   - This provides them with a new authentication token for the session.

### User Management
3. **Profile Access**: Once authenticated, users can view their profile details using the `/api/users/me` endpoint.
   - This returns basic user information like name and email.
4. **Profile Updates**: Users can modify their profile information through the `/api/users/update` endpoint.
   - This allows changes to name, email, or password.

### Core Financial Management
5. **Dashboard Overview**: Users get a financial summary through the `/api/dashboard/summary` endpoint.
   - This provides high-level metrics like total income, expenses, and savings rate.

### Transaction Management
6. The core of the application revolves around transaction tracking:
   - Users can view all transactions (`GET /api/transactions`)
   - View specific transaction details (`GET /api/transactions/:id`)
   - Add new transactions (`POST /api/transactions`)
   - Update existing transactions (`PUT /api/transactions/:id`)
   - Delete transactions (`DELETE /api/transactions/:id`)

### Budget Management
7. Users can set spending limits through budget endpoints:
   - View all active budgets (`GET /api/budgets`)
   - Get details of specific budgets (`GET /api/budgets/:id`)
   - Create new budgets (`POST /api/budgets`)
   - Modify existing budgets (`PUT /api/budgets/:id`)
   - Remove budgets (`DELETE /api/budgets/:id`)

### Financial Goals
8. For longer-term financial planning:
   - View all financial goals (`GET /api/goals`)
   - Access specific goal details (`GET /api/goals/:id`)
   - Set new financial goals (`POST /api/goals`)
   - Update progress on goals (`PUT /api/goals/:id`)
   - Remove goals (`DELETE /api/goals/:id`)

### Financial Analysis
9. Users can generate various financial insights:
   - Compare income versus expenses (`GET /api/reports/income-vs-expenses`)
   - Analyze spending trends over time (`GET /api/reports/spending-trends`)
   - Review budget performance (`GET /api/reports/budget-performance`)

### Typical User Journey
1. A user registers or logs in
2. They view their dashboard for a financial overview
3. They record new transactions as they occur
4. They set up budgets to control spending in different categories (SK Control later)
5. They establish financial goals for larger future objectives (SK Control later)
6. They regularly check reports to analyze their financial patterns and progress (SK Control later)
7. They adjust budgets and goals based on their performance and changing needs (SK Control later)

## Authentication Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/auth/signup` | POST | Register a new user | `{ email, password, name }` | `{ message, token, user: { id, name, email } }` |
| `/api/auth/login` | POST | Log in a user | `{ email, password }` | `{ message, token, user: { id, name, email } }` |

## User Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/users/me` | GET | Get current user profile | Auth token in header | `{ user: { id, name, email } }` |
| `/api/users/update` | PUT | Update user profile | Auth token, `{ name, email, password? }` | `{ message, user: { id, name, email } }` |

## Dashboard Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/dashboard/summary` | GET | Get financial summary | Auth token | `{ totalIncome, totalExpenses, netIncome, savingsRate }` |

## Transactions Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/transactions` | GET | Get all transactions | Auth token, optional query params | `{ transactions: [{ id, amount, description, category, date, type }] }` |
| `/api/transactions/:id` | GET | Get a specific transaction | Auth token, transaction ID | `{ transaction: { id, amount, description, category, date, type } }` |
| `/api/transactions` | POST | Create a new transaction | Auth token, `{ amount, description, category, date, type }` | `{ message, transaction: { id, amount, description, category, date, type } }` |
| `/api/transactions/:id` | PUT | Update a transaction | Auth token, transaction ID, transaction data | `{ message, transaction: { id, amount, description, category, date, type } }` |
| `/api/transactions/:id` | DELETE | Delete a transaction | Auth token, transaction ID | `{ message, id }` |

## Budgets Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/budgets` | GET | Get all budgets | Auth token | `{ budgets: [{ id, name, amount, period, category, currentSpending }] }` |
| `/api/budgets/:id` | GET | Get a specific budget | Auth token, budget ID | `{ budget: { id, name, amount, period, category, currentSpending } }` |
| `/api/budgets` | POST | Create a new budget | Auth token, `{ name, amount, period, category }` | `{ message, budget: { id, name, amount, period, category, currentSpending } }` |
| `/api/budgets/:id` | PUT | Update a budget | Auth token, budget ID, budget data | `{ message, budget: { id, name, amount, period, category, currentSpending } }` |
| `/api/budgets/:id` | DELETE | Delete a budget | Auth token, budget ID | `{ message, id }` |

## Goals Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/goals` | GET | Get all financial goals | Auth token | `{ goals: [{ id, name, targetAmount, currentAmount, targetDate, category }] }` |
| `/api/goals/:id` | GET | Get a specific goal | Auth token, goal ID | `{ goal: { id, name, targetAmount, currentAmount, targetDate, category } }` |
| `/api/goals` | POST | Create a new goal | Auth token, `{ name, targetAmount, currentAmount, targetDate, category }` | `{ message, goal: { id, name, targetAmount, currentAmount, targetDate, category } }` |
| `/api/goals/:id` | PUT | Update a goal | Auth token, goal ID, goal data | `{ message, goal: { id, name, targetAmount, currentAmount, targetDate, category } }` |
| `/api/goals/:id` | DELETE | Delete a goal | Auth token, goal ID | `{ message, id }` |

## Reports Routes

| Route | Method | Description | Input | Output |
|-------|--------|-------------|-------|--------|
| `/api/reports/income-vs-expenses` | GET | Get income vs expenses | Auth token, `{ startDate, endDate }` | `{ totalIncome, totalExpenses, netIncome, incomeByCategory, expensesByCategory }` |
| `/api/reports/spending-trends` | GET | Get spending trends | Auth token, `{ startDate, endDate, period }` | `{ trends: [{ period, amount }] }` |
| `/api/reports/budget-performance` | GET | Get budget performance | Auth token | `{ budgets: [{ id, name, amount, spent, remaining, percentUsed }] }` |
