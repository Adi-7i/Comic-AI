import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function PricingPage() {
    const plans = [
        {
            name: "Free",
            price: "$0",
            description: "For hobbyists and experimenters.",
            features: ["3 Comics per month", "Standard Quality", "Watermarked", "Public Gallery"],
            cta: "Current Plan",
            variant: "outline"
        },
        {
            name: "Pro",
            price: "$15",
            description: "For creators who want more power.",
            features: ["50 Comics per month", "High Quality", "No Watermark", "Private Gallery", "Priority Generation"],
            cta: "Upgrade to Pro",
            variant: "default",
            popular: true
        },
        {
            name: "Creative",
            price: "$29",
            description: "For serious storytellers and agencies.",
            features: ["Unlimited Comics", "Ultra Quality", "Custom Styles", "Commercial License", "API Access"],
            cta: "Contact Sales",
            variant: "outline"
        }
    ];

    return (
        <div className="py-12 max-w-5xl mx-auto">
            <div className="text-center mb-12 space-y-4">
                <h1 className="text-4xl font-bold tracking-tight">Simple, Transparent Pricing</h1>
                <p className="text-xl text-muted-foreground">Choose the plan that best fits your creative journey.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {plans.map((plan) => (
                    <Card key={plan.name} className={`flex flex-col relative ${plan.popular ? 'border-indigo-500 shadow-lg scale-105 z-10' : ''}`}>
                        {plan.popular && (
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                                Most Popular
                            </div>
                        )}
                        <CardHeader>
                            <CardTitle className="text-2xl">{plan.name}</CardTitle>
                            <div className="mt-2">
                                <span className="text-4xl font-bold">{plan.price}</span>
                                <span className="text-muted-foreground">/mo</span>
                            </div>
                            <CardDescription>{plan.description}</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1">
                            <ul className="space-y-3">
                                {plan.features.map((feature) => (
                                    <li key={feature} className="flex items-center gap-2 text-sm">
                                        <Check className="h-4 w-4 text-green-500" />
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                        <CardFooter>
                            <Button className="w-full" variant={plan.variant as "default" | "outline"}>
                                {plan.cta}
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
}
