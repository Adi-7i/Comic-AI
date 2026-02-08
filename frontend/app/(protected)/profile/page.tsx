"use client";

import { ProfileCard } from "@/components/profile/profile-card";
import { UsageCard } from "@/components/profile/usage-card";
import { ProfileSkeleton } from "@/components/ui/skeletons";
import { useState, useEffect } from "react";

export default function ProfilePage() {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simulate loading delight
        const timer = setTimeout(() => setIsLoading(false), 800);
        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return <ProfileSkeleton />;
    }

    return (
        <div className="space-y-8 max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2">My Profile</h1>
                <p className="text-muted-foreground">Manage your account settings and preferences.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2">
                    <ProfileCard
                        name="Alex Chen"
                        email="alex.chen@example.com"
                        plan="Pro"
                    />
                </div>
                <div>
                    <UsageCard
                        plan="Pro"
                        usage={{
                            comicsCreated: 12,
                            comicsLimit: 50,
                            pagesGenerated: 48
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
