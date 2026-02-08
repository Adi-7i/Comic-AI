"use client";

import { ProfileCard } from "@/components/profile/profile-card";
import { UsageCard } from "@/components/profile/usage-card";
import { ProfileSkeleton } from "@/components/ui/skeletons";
import { useState, useEffect } from "react";
import { authApi } from "@/lib/api/auth";
import { profileApi } from "@/lib/api/profile";
import { User, Usage } from "@/lib/types/api";

export default function ProfilePage() {
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState<User | null>(null);
    const [usage, setUsage] = useState<Usage | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [userData, usageData] = await Promise.all([
                    authApi.getUserProfile(),
                    profileApi.getUsage()
                ]);
                setUser(userData);
                setUsage(usageData);
            } catch (error) {
                console.error("Failed to load profile data", error);
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);

    if (isLoading || !user || !usage) {
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
                        name={user.name}
                        email={user.email}
                        plan={user.plan}
                    />
                </div>
                <div>
                    <UsageCard
                        usage={usage}
                    />
                </div>
            </div>
        </div>
    );
}
