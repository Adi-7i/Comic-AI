import { Button } from "@/components/ui/button";
import { Layout, PenTool, CreditCard, Sparkles, ArrowRight } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { ProjectCard } from "@/components/dashboard/project-card";

export default function DashboardPage() {

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                {/* Stats Overview */}
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Welcome back, Alex!</h1> {/* Name changed */}
                    <p className="text-muted-foreground">Here&apos;s what&apos;s happening with your projects.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"> {/* Grid layout changed */}
                <StatCard
                    title="Total Comics"
                    value="12"
                    icon={Layout} // Icon changed
                    trend="+2 this week" // Description changed
                />
                <StatCard
                    title="Stories Used"
                    value="8"
                    icon={PenTool} // Icon changed
                    description="Limit: 20/mo" // Description changed
                />
                <StatCard
                    title="Current Plan"
                    value="Pro"
                    icon={CreditCard} // Icon changed
                    trend="kudos! 🚀" // Description changed
                />
                <StatCard
                    title="Credits"
                    value="350"
                    icon={Sparkles} // Icon changed
                    description="Expires in 14 days" // Description changed
                />
            </div>

            {/* Recent Creating / Projects */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold tracking-tight">Recent Projects</h2>
                    <Button variant="ghost" size="sm" className="hidden sm:flex"> {/* Button variant changed */}
                        View All <ArrowRight className="ml-2 h-4 w-4" /> {/* Icon added */}
                    </Button>
                </div>

                {/* Project List / Grid */}
                {/* <EmptyState /> */} {/* EmptyState commented out */}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"> {/* Grid layout changed */}
                    <ProjectCard
                        title="The Galactic Adventures of Robo-Cat"
                        updatedAt="2 hours ago"
                        status="Generating"
                        thumbnail="https://images.unsplash.com/photo-1614728853913-3e320436d400?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZnV0dXJpc3RpYyUyMGNpdHl8ZW58MHx8MHx8fDA%3D" // Thumbnail changed
                    />
                    <ProjectCard
                        title="Midnight Noir: detective diaries"
                        updatedAt="1 day ago"
                        status="Draft"
                        thumbnail="https://images.unsplash.com/photo-1655198696803-12239f67a2a1?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGRldGljdGl2ZSUyMG5vaXJ8ZW58MHx8MHx8fDA%3D" // Thumbnail changed
                    />
                    <ProjectCard
                        title="Fantasy Quest: The Lost Sword"
                        updatedAt="3 days ago"
                        status="Completed"
                        thumbnail="https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8ZmFudGFzeSUyMGxhbmRzY2FwZXxlbnwwfHwwfHx8MA%3D%3D" // Thumbnail changed
                    />
                </div>
                <div className="mt-8 flex justify-center sm:hidden"> {/* New button for mobile */}
                    <Button variant="outline" className="w-full">
                        View All Projects
                    </Button>
                </div>
            </div>
        </div>
    );
}
