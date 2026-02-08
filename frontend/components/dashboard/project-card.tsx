import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, MoreHorizontal, ArrowRight } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ProjectCardProps {
    title: string;
    updatedAt: string;
    status: "Draft" | "Generating" | "Completed";
    thumbnail?: string;
}

export function ProjectCard({ title, updatedAt, status, thumbnail }: ProjectCardProps) {
    const statusColor = {
        Draft: "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-300",
        Generating: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 animate-pulse",
        Completed: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
    };

    return (
        <Card className="group overflow-hidden border-zinc-200 dark:border-zinc-800 hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300">
            <div className="aspect-video relative bg-zinc-100 dark:bg-zinc-900 w-full overflow-hidden">
                {thumbnail ? (
                    <div className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105" style={{ backgroundImage: `url(${thumbnail})` }} />
                ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-zinc-300 dark:text-zinc-700">
                        <div className="w-16 h-16 bg-zinc-200 dark:bg-zinc-800 rounded-full flex items-center justify-center">
                            <span className="text-2xl">🎨</span>
                        </div>
                    </div>
                )}
                <div className="absolute top-3 right-3">
                    <Badge variant="secondary" className={statusColor[status]}>{status}</Badge>
                </div>
            </div>

            <CardContent className="p-4">
                <h3 className="font-semibold text-lg line-clamp-1 group-hover:text-indigo-500 transition-colors">{title}</h3>
                <div className="flex items-center text-xs text-muted-foreground mt-2">
                    <Clock className="w-3 h-3 mr-1" />
                    <span>Edited {updatedAt}</span>
                </div>
            </CardContent>

            <CardFooter className="p-4 pt-0 flex justify-between items-center">
                <Button variant="ghost" size="sm" className="text-zinc-500 hover:text-indigo-500 p-0 hover:bg-transparent">
                    View Details <ArrowRight className="w-4 h-4 ml-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                </Button>

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
                            <MoreHorizontal className="w-4 h-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem>Rename</DropdownMenuItem>
                        <DropdownMenuItem>Duplicate</DropdownMenuItem>
                        <DropdownMenuItem className="text-red-500 focus:text-red-500">Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </CardFooter>
        </Card>
    );
}
