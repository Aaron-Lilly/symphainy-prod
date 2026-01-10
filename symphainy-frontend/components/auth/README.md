# Authentication System

This is a complete authentication system with login and registration functionality using shadcn components.

## Components

### LoginForm

A complete login form with email/password validation and registration link.

```tsx
import LoginForm from "@/components/auth/login-form";

<LoginForm
  onLoginSuccess={(user, token) => {
    // Handle successful login
  }}
  onLoginError={(error) => {
    // Handle login error
  }}
  onSwitchToRegister={() => {
    // Switch to registration mode
  }}
/>;
```

### RegisterForm

A complete registration form with name/email/password validation and login link.

```tsx
import RegisterForm from "@/components/auth/register-form";

<RegisterForm
  onRegisterSuccess={(user, token) => {
    // Handle successful registration
  }}
  onRegisterError={(error) => {
    // Handle registration error
  }}
  onSwitchToLogin={() => {
    // Switch to login mode
  }}
/>;
```

### AuthGuard

Authentication wrapper that protects routes and redirects unauthenticated users.

```tsx
import AuthGuard from "@/components/auth/auth-guard";

<AuthGuard>{/* Protected content */}</AuthGuard>;
```

### LogoutButton

A button component for logging out users.

```tsx
import LogoutButton from "@/components/auth/logout-button";

<LogoutButton variant="outline" size="sm" />;
```

### AuthCard

A reusable card component for authentication forms.

```tsx
import { AuthCard } from "@/components/ui/auth-card";

<AuthCard title="Sign In" description="Enter your credentials">
  {/* Form content */}
</AuthCard>;
```

## API Functions

### loginUser(credentials)

Authenticates user with email and password.

```tsx
import { loginUser } from "@/lib/api/auth";

const response = await loginUser({ email, password });
```

### registerUser(credentials)

Registers a new user with name, email and password.

```tsx
import { registerUser } from "@/lib/api/auth";

const response = await registerUser({ name, email, password });
```

### Validation Functions

```tsx
import { validateEmail, validatePassword, validateName } from "@/lib/api/auth";

const emailValidation = validateEmail(email);
const passwordValidation = validatePassword(password);
const nameValidation = validateName(name);
```

## Utility Functions

```tsx
import {
  isAuthenticated,
  getCurrentUser,
  getAuthToken,
  clearAuth,
} from "@/lib/auth-utils";

// Check if user is logged in
const isLoggedIn = isAuthenticated();

// Get current user data
const user = getCurrentUser();

// Get auth token
const token = getAuthToken();

// Logout user
clearAuth();
```

## Demo Credentials

- **Admin:** admin@symphainy.com / admin123
- **User:** user@symphainy.com / user123
- **Demo:** demo@symphainy.com / demo123

## Usage

1. **Unauthenticated users** are automatically redirected to `/login`
2. Visit `/login` to access both login and registration forms
3. **Login** with demo credentials or **register** a new account
4. Successfully authenticated users are redirected to `/`
5. User data is stored in localStorage
6. Use `LogoutButton` component to log out

## Features

- ✅ **Login & Registration** - Complete authentication flow
- ✅ **Route Protection** - AuthGuard automatically protects all routes
- ✅ **Form Validation** - Email, password, and name validation with real-time feedback
- ✅ **Show/Hide Password** - Toggle visibility for password fields
- ✅ **Loading States** - Visual feedback during authentication requests
- ✅ **Error Handling** - Comprehensive error display and messaging
- ✅ **Auto-redirect** - Seamless navigation between auth states
- ✅ **Responsive Design** - Mobile-friendly authentication forms
- ✅ **Dummy Authentication** - In-memory user storage for development
- ✅ **TypeScript Support** - Full type safety throughout

## Next Steps (Future Implementation)

- [ ] Session management
- [ ] JWT token handling
- [ ] Real API integration
- [ ] Role-based access control
- [ ] Password reset functionality
- [ ] Remember me functionality
