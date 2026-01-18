"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LoginForm, RegisterForm } from "@/components/auth";
import { useAuth } from "@/shared/auth/AuthProvider";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const { login, register } = useAuth();

  const handleAuthSuccess = async (user: any, token: string) => {
    console.log("Auth successful:", { user, token });

    // The AuthProvider will handle storing the auth data
    // Redirect to main page after successful auth
    router.push("/");
  };

  const handleAuthError = (error: string) => {
    console.error("Auth error:", error);
  };

  if (mode === "register") {
    return (
      <RegisterForm
        onRegisterSuccess={handleAuthSuccess}
        onRegisterError={handleAuthError}
        onSwitchToLogin={() => setMode("login")}
      />
    );
  }

  return (
    <LoginForm
      onLoginSuccess={handleAuthSuccess}
      onLoginError={handleAuthError}
      onSwitchToRegister={() => setMode("register")}
    />
  );
}
