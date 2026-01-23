"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface DropdownMenuProps {
  children: React.ReactNode;
}

interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  children: React.ReactNode;
}

interface DropdownMenuContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: "start" | "end" | "center";
}

interface DropdownMenuItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  onSelect?: (event: React.SyntheticEvent<HTMLButtonElement>) => void;
}

const DropdownMenuContext = React.createContext<{
  open: boolean;
  setOpen: (open: boolean) => void;
}>({ open: false, setOpen: () => {} });

const DropdownMenu: React.FC<DropdownMenuProps> = ({ children }) => {
  const [open, setOpen] = React.useState(false);

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  );
};

const DropdownMenuTrigger = React.forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ className, children, asChild, ...props }, ref) => {
    const { setOpen } = React.useContext(DropdownMenuContext);

    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children as React.ReactElement<any>, {
        ...props,
        onClick: (e: React.MouseEvent<any>) => {
          setOpen(true);
          props.onClick?.(e as React.MouseEvent<HTMLButtonElement>);
        },
      });
    }

    return (
      <button
        ref={ref}
        type="button"
        className={cn(
          "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium",
          "bg-white border border-gray-300 hover:bg-gray-50",
          className
        )}
        onClick={() => setOpen(true)}
        {...props}
      >
        {children}
      </button>
    );
  }
);
DropdownMenuTrigger.displayName = "DropdownMenuTrigger";

const DropdownMenuContent = React.forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ className, children, align = "end", ...props }, ref) => {
    const { open, setOpen } = React.useContext(DropdownMenuContext);
    const contentRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
          setOpen(false);
        }
      };

      if (open) {
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
      }
    }, [open, setOpen]);

    if (!open) return null;

    const alignClasses = {
      start: "left-0",
      end: "right-0",
      center: "left-1/2 -translate-x-1/2",
    };

    return (
      <div
        ref={contentRef}
        className={cn(
          "absolute z-50 mt-2 min-w-[8rem] rounded-md border bg-white shadow-lg",
          alignClasses[align],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
DropdownMenuContent.displayName = "DropdownMenuContent";

const DropdownMenuItem = React.forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
  ({ className, children, onSelect, ...props }, ref) => {
    const { setOpen } = React.useContext(DropdownMenuContext);

    return (
      <button
        ref={ref}
        type="button"
        className={cn(
          "relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm",
          "hover:bg-gray-100 focus:bg-gray-100",
          className
        )}
        onClick={(e) => {
          setOpen(false);
          onSelect?.(e);
          props.onClick?.(e);
        }}
        {...props}
      >
        {children}
      </button>
    );
  }
);
DropdownMenuItem.displayName = "DropdownMenuItem";

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
};
