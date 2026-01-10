"use client";

import React from "react";
import { useAuth } from "@/shared/agui/AuthProvider";
import { LogoutButton } from "@/components/auth";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function AuthStatus() {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Don't render if not authenticated or still loading
  if (isLoading || !isAuthenticated || !user) {
    return null;
  }

  // Get user initials for avatar (defensive check for undefined name)
  const userName = user.name || user.email || "User";
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <div className="flex items-center space-x-3 text-sm text-gray-600">
      <Avatar>
        <AvatarImage src={user.avatar_url} />
        <AvatarFallback>{userInitial}</AvatarFallback>
      </Avatar>
      <span className="hidden md:block">Welcome, {userName}</span>
      <LogoutButton variant="outline" size="sm" />
    </div>
  );
}
