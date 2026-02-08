import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { User, LogOut, Settings, CreditCard } from "lucide-react";
import { PlanType } from "@/lib/store/wizard-store";

interface ProfileCardProps {
    name: string;
    email: string;
    avatar?: string;
    plan: PlanType;
}

export function ProfileCard({ name, email, avatar, plan }: ProfileCardProps) {
    const planColors = {
        Free: "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-300",
        Pro: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400",
        Creative: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400"
    };

    return (
        <Card>
            <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <Avatar className="w-16 h-16 border-2 border-white dark:border-zinc-800 shadow-sm">
                    <AvatarImage src={avatar} alt={name} />
                    <AvatarFallback className="bg-gradient-to-br from-indigo-500 to-purple-500 text-white text-xl">
                        {name.charAt(0)}
                    </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <CardTitle className="text-xl">{name}</CardTitle>
                        <Badge variant="secondary" className={planColors[plan]}>{plan}</Badge>
                    </div>
                    <CardDescription>{email}</CardDescription>
                </div>
            </CardHeader>
            <CardContent className="pt-4 grid gap-3">
                <Button variant="outline" className="justify-start">
                    <User className="mr-2 h-4 w-4" /> Personal Information
                </Button>
                <Button variant="outline" className="justify-start">
                    <Settings className="mr-2 h-4 w-4" /> Account Settings
                </Button>
                <Button variant="outline" className="justify-start">
                    <CreditCard className="mr-2 h-4 w-4" /> Billing & Invoices
                </Button>
                <div className="pt-2">
                    <Button variant="ghost" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/20">
                        <LogOut className="mr-2 h-4 w-4" /> Sign Out
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
