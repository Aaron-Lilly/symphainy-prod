"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AuthCard } from "@/components/ui/auth-card";
import { Loader2, Eye, EyeOff, Mail, Lock } from "lucide-react";
import { validateEmail, validatePassword } from "@/lib/api/auth";
import { useAuth } from "@/shared/auth/AuthProvider";

interface LoginFormProps {
  onLoginSuccess?: (user: any, token: string) => void;
  onLoginError?: (error: string) => void;
  onSwitchToRegister?: () => void;
}

export default function LoginForm({
  onLoginSuccess,
  onLoginError,
  onSwitchToRegister,
}: LoginFormProps) {
  const { login, isLoading, error, user, sessionToken } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    general?: string;
  }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});

    // Validate email and password
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    const newErrors: { email?: string; password?: string } = {};

    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.message;
    }

    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.message;
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      await login(email, password);
      // Login successful - AuthProvider handles state
      // Wait a moment for state to update, then check
      setTimeout(() => {
        if (user && sessionToken) {
          onLoginSuccess?.(user, sessionToken);
        }
      }, 100);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unexpected error occurred. Please try again.";
      setErrors({ general: errorMessage });
      onLoginError?.(errorMessage);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <AuthCard
        title="Sign in"
        description="Enter your email and password to access your account"
        className="w-full max-w-md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div className="space-y-2">
            <label
              htmlFor="email"
              className="text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`pl-10 ${errors.email ? "border-red-500 focus:border-red-500" : ""}`}
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </div>
            {errors.email && (
              <p className="text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          {/* Password Input */}
          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                className={`pl-10 pr-10 ${errors.password ? "border-red-500 focus:border-red-500" : ""}`}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="button"
                className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-sm text-red-600">{errors.password}</p>
            )}
          </div>

          {/* General Error */}
          {errors.general && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-600">{errors.general}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Signing in...
              </>
            ) : (
              "Login"
            )}
          </Button>

          {/* Switch to Register */}
          {onSwitchToRegister && (
            <div className="text-center mt-4">
              <p className="text-sm text-gray-600">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={onSwitchToRegister}
                  className="font-medium text-primary hover:text-primary/80 underline"
                  disabled={isLoading}
                >
                  Create account here
                </button>
              </p>
            </div>
          )}

          {/* Demo Credentials */}
          {/* <div className="mt-6 p-4 bg-blue-50 rounded-md">
            <p className="text-sm font-medium text-blue-800 mb-2">Demo Credentials:</p>
            <div className="text-xs text-blue-600 space-y-1">
              <p><strong>Admin:</strong> admin@symphainy.com / admin123</p>
              <p><strong>User:</strong> user@symphainy.com / user123</p>
              <p><strong>Demo:</strong> demo@symphainy.com / demo123</p>
            </div>
          </div> */}
        </form>
      </AuthCard>
    </div>
  );
}
