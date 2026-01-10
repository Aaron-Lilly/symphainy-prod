"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { useAuth } from "@/shared/agui/AuthProvider";

interface LogoutButtonProps {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
  showIcon?: boolean;
  children?: React.ReactNode;
}

export default function LogoutButton({
  variant = "outline",
  size = "sm",
  className,
  showIcon = true,
  children,
}: LogoutButtonProps) {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      // Use AuthProvider logout method
      await logout();
      
      // Redirect to login page
      router.push("/login");
      
      console.log("User logged out successfully");
    } catch (error) {
      console.error("Logout error:", error);
      // Still redirect even if logout fails
      router.push("/login");
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleLogout}
      className={className}
    >
      {showIcon && <LogOut className="h-4 w-4" />}
      {/* {children || 'Logout'} */}
    </Button>
  );
}
