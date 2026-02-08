import { useWizardStore, PlanType } from "@/lib/store/wizard-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, Zap, Crown, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export function PlanSelection() {
    const { selectedPlan, setPlan, setStep } = useWizardStore();

    const plans = [
        {
            id: "Free",
            name: "Free Tier",
            icon: Zap,
            features: ["1 Comic / Day", "Watermarked", "Standard Resolution", "Basic Styles"],
            color: "text-zinc-500",
            borderColor: "border-zinc-200 dark:border-zinc-800",
        },
        {
            id: "Pro",
            name: "Pro Plan",
            icon: Crown,
            features: ["10 Comics / Day", "No Watermark", "HD Resolution", "All Styles"],
            color: "text-indigo-500",
            borderColor: "border-indigo-500/50",
            popular: true,
        },
        {
            id: "Creative",
            name: "Creative Limitless",
            icon: Sparkles,
            features: ["Unlimited Comics", "Commercial Rights", "4K Ultra HD", "Priority Support"],
            color: "text-pink-500",
            borderColor: "border-pink-500/50",
        },
    ];

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-6">
                {plans.map((plan) => {
                    const isSelected = selectedPlan === plan.id;
                    const Icon = plan.icon;

                    return (
                        <Card
                            key={plan.id}
                            className={cn(
                                "relative cursor-pointer transition-all duration-300 hover:shadow-lg",
                                isSelected
                                    ? `ring-2 ring-offset-2 ring-indigo-500 ${plan.borderColor} dark:ring-offset-zinc-900`
                                    : "hover:border-zinc-400 dark:hover:border-zinc-600"
                            )}
                            onClick={() => setPlan(plan.id as PlanType)}
                        >
                            {plan.popular && (
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-[10px] font-bold uppercase tracking-wide px-3 py-1 rounded-full shadow-sm">
                                    Most Popular
                                </div>
                            )}
                            <CardHeader>
                                <Icon className={cn("w-8 h-8 mb-2", plan.color)} />
                                <CardTitle>{plan.name}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    {plan.features.map((feature, i) => (
                                        <li key={i} className="flex items-center text-sm text-muted-foreground">
                                            <Check className="w-4 h-4 mr-2 text-green-500" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <div className="flex justify-end pt-4">
                <Button
                    onClick={() => setStep(2)}
                    disabled={!selectedPlan}
                    className="w-full md:w-auto bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
                >
                    Continue
                </Button>
            </div>
        </div>
    );
}
