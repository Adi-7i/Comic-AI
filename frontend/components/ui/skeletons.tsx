import { Skeleton } from "@/components/ui/skeleton";

export function ProjectCardSkeleton() {
    return (
        <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 bg-card text-card-foreground shadow-sm">
            <div className="aspect-video w-full bg-zinc-100 dark:bg-zinc-800 animate-pulse rounded-t-xl" />
            <div className="p-4 space-y-3">
                <Skeleton className="h-5 w-3/4" />
                <div className="flex justify-between items-center pt-2">
                    <Skeleton className="h-4 w-1/4" />
                    <Skeleton className="h-8 w-8 rounded-full" />
                </div>
            </div>
        </div>
    );
}

export function DashboardSkeleton() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-2">
                    <Skeleton className="h-8 w-48" />
                    <Skeleton className="h-4 w-64" />
                </div>
                <Skeleton className="h-10 w-32" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} className="h-32 rounded-xl" />
                ))}
            </div>

            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <Skeleton className="h-6 w-32" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(3)].map((_, i) => (
                        <ProjectCardSkeleton key={i} />
                    ))}
                </div>
            </div>
        </div>
    );
}

export function ProfileSkeleton() {
    return (
        <div className="space-y-8 max-w-5xl mx-auto">
            <div className="space-y-2">
                <Skeleton className="h-8 w-32" />
                <Skeleton className="h-4 w-48" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2">
                    <Skeleton className="h-64 w-full rounded-xl" />
                </div>
                <div>
                    <Skeleton className="h-64 w-full rounded-xl" />
                </div>
            </div>
        </div>
    );
}
