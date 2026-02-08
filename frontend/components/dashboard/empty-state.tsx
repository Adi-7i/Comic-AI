import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export function EmptyState() {
    return (
        <div className="flex flex-col items-center justify-center p-8 md:p-12 border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/50 text-center animate-in fade-in-50 duration-500">
            <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mb-4">
                <Plus className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Create your first comic</h3>
            <p className="text-muted-foreground max-w-sm mb-6">
                You haven&apos;t created any projects yet. Start by creating a new comic project to bring your stories to life.
            </p>
            <Button className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white shadow-lg shadow-indigo-500/20">
                <Plus className="h-4 w-4 mr-2" />
                Create New Comic
            </Button>
        </div>
    );
}
