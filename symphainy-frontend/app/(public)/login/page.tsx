"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LoginForm, RegisterForm } from "@/components/auth";
import { useAuth } from "@/shared/auth/AuthProvider";
import { useTenant } from "@/shared/contexts/TenantContext";
import { TenantId } from "@/shared/config/tenant-types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const { login, register } = useAuth();
  const { setTenant, availableTenants, tenantId, currentTenant } = useTenant();

  const handleTenantChange = (value: string) => {
    setTenant(value as TenantId);
  };

  const handleAuthSuccess = async (user: any, token: string) => {
    console.log("Auth successful:", { user, token, tenant: tenantId });
    router.push("/");
  };

  const handleAuthError = (error: string) => {
    console.error("Auth error:", error);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">SymphAIny Platform</CardTitle>
          <CardDescription>
            Select your demo environment and sign in
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Tenant Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Demo Environment
            </label>
            <Select value={tenantId} onValueChange={handleTenantChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select demo environment" />
              </SelectTrigger>
              <SelectContent>
                {availableTenants.map((tenant) => (
                  <SelectItem key={tenant.id} value={tenant.id}>
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{tenant.name}</span>
                      <span className="text-xs text-gray-500">{tenant.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {/* Show current tenant welcome message preview */}
            {currentTenant.branding?.welcome_message && (
              <p className="text-xs text-gray-500 italic mt-2">
                {currentTenant.branding.welcome_message}
              </p>
            )}
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">
                {mode === "login" ? "Sign in to continue" : "Create account"}
              </span>
            </div>
          </div>

          {/* Auth Form */}
          {mode === "register" ? (
            <RegisterForm
              onRegisterSuccess={handleAuthSuccess}
              onRegisterError={handleAuthError}
              onSwitchToLogin={() => setMode("login")}
            />
          ) : (
            <LoginForm
              onLoginSuccess={handleAuthSuccess}
              onLoginError={handleAuthError}
              onSwitchToRegister={() => setMode("register")}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
