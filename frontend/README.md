# Hospital Management System - Frontend

A modern React-based interactive dashboard for managing hospital operations.

## Features

- **Patient Management**: Register and manage patient information
- **Appointment Scheduling**: Schedule and cancel appointments
- **Billing System**: Create and track billing records
- **Inventory Management**: Track medical supplies and equipment

## Installation

```bash
cd frontend
npm install
```

## Running the Frontend

```bash
npm start
```

The app will open at `http://localhost:3000`

## Requirements

- Node.js 14+
- npm or yarn
- Backend API running on `http://localhost:8000`

## Build for Production

```bash
npm run build
```

## Technologies Used

- React 18
- Axios for API calls
- CSS3 for styling
- React Router for navigation

## API Integration

The frontend connects to the backend API at `http://localhost:8000`. Make sure the backend is running before starting the frontend.

## Features Overview

### Patients Tab
- Add new patients with demographic information
- View all registered patients
- Track patient status

### Appointments Tab
- Schedule appointments with date/time
- View all scheduled appointments
- Cancel appointments

### Billing Tab
- Create billing records for services
- Track total billing amount
- View billing history

### Inventory Tab
- Add medical supplies and equipment
- Track inventory quantities and costs
- Monitor total inventory value
- Track expiration dates
