# Project149 Frontend

React frontend for the e-commerce recommendation system.

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure API URL:
```bash
cp .env.example .env
# Edit .env if your backend runs on a different port
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Features

- User authentication (signup/login)
- Product browsing and search
- Product details with interaction tracking
- Shopping cart management
- Checkout and order placement
- Order history
- Personalized recommendations

## Tech Stack

- React 18
- Vite
- React Router DOM
- Axios
- Tailwind CSS
- Day.js

## Project Structure

```
src/
├── api/
│   └── axios.js          # Axios instance with auth interceptor
├── auth/
│   ├── Login.jsx         # Login page
│   ├── Signup.jsx        # Signup page
│   └── auth.js           # Auth helpers (token management)
├── components/
│   ├── NavBar.jsx        # Navigation bar
│   ├── ProductCard.jsx   # Product card component
│   └── ProtectedRoute.jsx # Route protection wrapper
├── pages/
│   ├── Home.jsx          # Product listing + recommendations
│   ├── Product.jsx       # Product details
│   ├── Cart.jsx          # Shopping cart
│   ├── Checkout.jsx      # Checkout page
│   ├── Orders.jsx        # Order history
│   └── Recommendations.jsx # Personalized recommendations
├── App.jsx               # Main app with routing
├── main.jsx              # Entry point
└── index.css             # Tailwind styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
