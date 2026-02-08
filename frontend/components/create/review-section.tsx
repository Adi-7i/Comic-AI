"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, FileText, Image as ImageIcon, Wand2, Save } from "lucide-react";

export function ReviewSection() {
    const { storyText, selectedPlan, setGenerationStatus } = useWizardStore();

    const handleGenerate = () => {
        if (!storyText.trim()) return;
        setGenerationStatus("processing");
    };

    const isReady = storyText.length > 20;

    return (
        <div className="space-y-4 pt-4 border-t border-zinc-200 dark:border-zinc-800">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold tracking-tight">Summary</h3>
                <span className="text-xs text-muted-foreground uppercase tracking-widest font-medium">
                    Ready to Create
                </span>
            </div>

            <Card className="p-4 bg-zinc-50 dark:bg-zinc-900/50 border-zinc-200 dark:border-zinc-800">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="space-y-1">
                        <span className="text-muted-foreground flex items-center gap-1.5 text-xs uppercase tracking-wider">
                            <FileText className="w-3.5 h-3.5" /> Plan
                        </span>
                        <p className="font-medium">{selectedPlan}</p>
                    </div>
                    <div className="space-y-1">
                        <span className="text-muted-foreground flex items-center gap-1.5 text-xs uppercase tracking-wider">
                            <ImageIcon className="w-3.5 h-3.5" /> Pages
                        </span>
                        <p className="font-medium">
                            {selectedPlan === "Free" ? "1 Page" : selectedPlan === "Pro" ? "3 Pages" : "Unlimited"}
                        </p>
                    </div>
                    <div className="space-y-1">
                        <span className="text-muted-foreground flex items-center gap-1.5 text-xs uppercase tracking-wider">
                            <Wand2 className="w-3.5 h-3.5" /> Style
                        </span>
                        <p className="font-medium">Auto-Detect</p>
                    </div>
                    <div className="space-y-1">
                        <span className="text-muted-foreground flex items-center gap-1.5 text-xs uppercase tracking-wider">
                            <Sparkles className="w-3.5 h-3.5" /> Status
                        </span>
                        <p className="font-medium text-green-600 dark:text-green-400">
                            {isReady ? "Ready" : "Waiting for story..."}
                        </p>
                    </div>
                </div>
            </Card>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <Button
                    className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/20 py-6 text-lg font-medium transition-all hover:scale-[1.02]"
                    disabled={!isReady}
                    onClick={handleGenerate}
                >
                    <Sparkles className="w-5 h-5 mr-2 animate-pulse" />
                    Generate Comic
                </Button>
                <Button
                    variant="outline"
                    className="py-6 text-base font-medium sm:w-40"
                    disabled={!isReady}
                >
                    <Save className="w-4 h-4 mr-2" />
                    Draft
                </Button>
            </div>
            <p className="text-center text-xs text-muted-foreground pt-2">
                This will use your monthly credits. {selectedPlan === "Free" ? "Upgrade for more." : ""}
            </p>
        </div>
    );
}
