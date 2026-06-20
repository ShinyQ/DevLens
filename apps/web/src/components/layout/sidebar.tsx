"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderGit2,
  MessageSquare,
  Wrench,
  DollarSign,
  Lightbulb,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Overview" },
  { href: "/repositories", icon: FolderGit2, label: "Repositories" },
  { href: "/sessions", icon: MessageSquare, label: "Sessions" },
  { href: "/tools", icon: Wrench, label: "Tools" },
  { href: "/costs", icon: DollarSign, label: "Costs" },
  { href: "/insights", icon: Lightbulb, label: "Insights" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-52 flex-col border-r border-zinc-800 bg-zinc-950 shrink-0">
      <div className="flex h-14 items-center gap-2.5 border-b border-zinc-800 px-4">
        <Cpu className="h-5 w-5 text-zinc-100" />
        <span className="text-sm font-semibold text-zinc-100">DevLens</span>
      </div>

      <nav className="flex-1 overflow-y-auto py-3">
        {navItems.map(({ href, icon: Icon, label }) => {
          const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 mx-2 mb-0.5 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-zinc-800 text-zinc-100"
                  : "text-zinc-500 hover:bg-zinc-800/60 hover:text-zinc-300"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-zinc-800 px-4 py-3">
        <p className="text-[10px] text-zinc-600 uppercase tracking-wider">Local &amp; Private</p>
      </div>
    </aside>
  );
}
