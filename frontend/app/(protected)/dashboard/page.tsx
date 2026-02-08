"use client";

import { Button } from "@/components/ui/button";
import { Layout, PenTool, CreditCard, Sparkles, ArrowRight } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { ProjectCard } from "@/components/dashboard/project-card";
import { useState, useEffect } from "react";
import { authApi } from "@/lib/api/auth";
import { projectsApi } from "@/lib/api/projects";
import { profileApi } from "@/lib/api/profile";
import { DashboardSkeleton } from "@/components/ui/skeletons";
import { User, Project, Usage, UsageStats } from "@/lib/types/api";

export default function DashboardPage() {
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState<User | null>(null);
    const [projects, setProjects] = useState<Project[]>([]);
    const [usage, setUsage] = useState<Usage | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [userData, projectsData, usageData] = await Promise.all([
                    authApi.getUserProfile(),
                    projectsApi.getRecentProjects(),
                    profileApi.getUsage()
                ]);
                setUser(userData);
                setProjects(projectsData);
                setUsage(usageData);
            } catch (error) {
                console.error("Failed to load dashboard data", error);
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);

    if (isLoading || !user || !usage) {
        return <DashboardSkeleton />;
    }

    // Safely access nested stats or fallback
    const stats: Partial<UsageStats> = usage.fullStats || {};

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                {/* Stats Overview */}
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user.name.split(' ')[0]}!</h1>
                    <p className="text-muted-foreground">Here&apos;s what&apos;s happening with your projects.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Comics"
                    value={stats.totalComics || "0"}
                    icon={Layout}
                    trend={stats.comicsTrend || "0 this week"}
                />
                <StatCard
                    title="Stories Used"
                    value={stats.storiesUsed || "0"}
                    icon={PenTool}
                    description={stats.storiesLimit || "0/mo"}
                />
                <StatCard
                    title="Current Plan"
                    value={stats.currentPlan || "Free"}
                    icon={CreditCard}
                    trend={stats.planTrend || ""}
                />
                <StatCard
                    title="Credits"
                    value={stats.credits || "0"}
                    icon={Sparkles}
                    description={stats.creditsExpiry || ""}
                />
            </div>

            {/* Recent Creating / Projects */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold tracking-tight">Recent Projects</h2>
                    <Button variant="ghost" size="sm" className="hidden sm:flex">
                        View All <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>

                {/* Project List / Grid */}
                {projects.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">No projects yet. Start creating!</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {projects.map((project: Project, index: number) => (
                            <ProjectCard
                                key={index}
                                title={project.title}
                                updatedAt={project.updatedAt}
                                status={project.status}
                                thumbnail={project.thumbnail}
                            />
                        ))}
                    </div>
                )}

                <div className="mt-8 flex justify-center sm:hidden">
                    <Button variant="outline" className="w-full">
                        View All Projects
                    </Button>
                </div>
            </div>
        </div>
    );
}
