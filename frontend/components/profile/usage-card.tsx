import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Zap, Sparkles } from "lucide-react";
import Link from "next/link";

interface UsageCardProps {
    usage: {
        comicsCreated: number;
        comicsLimit: number;
        pagesGenerated: number;
    };
}

export function UsageCard({ usage }: UsageCardProps) {
    const percentage = Math.min((usage.comicsCreated / usage.comicsLimit) * 100, 100);

    return (
        <Card className="h-full flex flex-col">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                    Usage Statistics
                </CardTitle>
                <CardDescription>
                    Your monthly generation limits and valid usage.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 flex-1">
                <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Comics Generated</span>
                        <span className="font-medium">{usage.comicsCreated} / {usage.comicsLimit}</span>
                    </div>
                    <Progress value={percentage} className="h-2" />
                    <p className="text-xs text-muted-foreground text-right pt-1">
                        Resets on Mar 1, 2026
                    </p>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="bg-zinc-50 dark:bg-zinc-900 p-3 rounded-lg border border-zinc-100 dark:border-zinc-800">
                        <span className="text-xs text-muted-foreground block mb-1">Total Pages</span>
                        <span className="text-2xl font-bold">{usage.pagesGenerated}</span>
                    </div>
                    <div className="bg-zinc-50 dark:bg-zinc-900 p-3 rounded-lg border border-zinc-100 dark:border-zinc-800">
                        <span className="text-xs text-muted-foreground block mb-1">Compute Hours</span>
                        <span className="text-2xl font-bold">1.2h</span>
                    </div>
                </div>
            </CardContent>
            <div className="p-6 pt-0 mt-auto">
                <Link href="/pricing" className="w-full">
                    <Button className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md">
                        <Sparkles className="w-4 h-4 mr-2" /> Upgrade Plan
                    </Button>
                </Link>
            </div>
        </Card>
    );
}
