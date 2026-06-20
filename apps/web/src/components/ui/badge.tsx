import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-zinc-700 text-zinc-100",
        outline: "border-zinc-700 text-zinc-400",
        blue: "border-transparent bg-blue-900/50 text-blue-300",
        green: "border-transparent bg-emerald-900/50 text-emerald-300",
        yellow: "border-transparent bg-yellow-900/50 text-yellow-300",
        red: "border-transparent bg-red-900/50 text-red-300",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
