"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Crown } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface StudioLayoutProps {
    children: React.ReactNode;
}

export function StudioLayout({ children }: StudioLayoutProps) {
    const { selectedPlan } = useWizardStore();

    return (
        <div className="min-h-screen bg-white dark:bg-zinc-950 flex flex-col">
            {/* Minimal Studio Header */}
            <header className="h-16 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between px-4 lg:px-8 bg-white/50 dark:bg-zinc-950/50 backdrop-blur-sm sticky top-0 z-30">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="icon" className="hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-full">
                            <ArrowLeft className="w-5 h-5 text-zinc-500" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-lg font-semibold tracking-tight p-0 animate-in fade-in slide-in-from-left-2 duration-500">
                            Create Your Comic
                        </h1>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground hidden sm:inline-block">
                        Creating as
                    </span>
                    <Badge variant="secondary" className="gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 dark:bg-indigo-950/30 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/50">
                        <Crown className="w-3.5 h-3.5" />
                        {selectedPlan} Plan
                    </Badge>
                </div>
            </header>

            {/* Main Studio Area */}
            <main className="flex-1 max-w-5xl w-full mx-auto p-4 lg:p-8 animate-in fade-in duration-700">
                {children}
            </main>
        </div>
    );
}
