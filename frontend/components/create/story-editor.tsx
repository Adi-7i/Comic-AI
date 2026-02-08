"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { Textarea } from "@/components/ui/textarea";
import { Sparkles, Info, CheckCircle2 } from "lucide-react";

import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";

export function StoryEditor() {
    const { storyText, setStory, selectedPlan } = useWizardStore();

    // Derived limits based on plan (UI logic only)
    const limits = {
        Free: { pages: 1, label: "1 page per comic" },
        Pro: { pages: 3, label: "Up to 3 pages" },
        Creative: { pages: 99, label: "Unlimited pages" }
    };

    const currentLimit = limits[selectedPlan || "Pro"];

    return (
        <div className="space-y-6">
            <div className="space-y-2">
                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center justify-between">
                    <span>Story Description</span>
                    <span className="text-xs text-muted-foreground bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded-full">
                        {storyText.length} chars
                    </span>
                </label>

                <div className="relative">
                    <Textarea
                        value={storyText}
                        onChange={(e) => setStory(e.target.value)}
                        placeholder="Write your story here... describe the setting, characters, and action clearly. For example: 'A cyberpunk detective explores a neon-lit alleyway in search of a missing droid...'"
                        className="min-h-[300px] text-lg leading-relaxed resize-none p-6 shadow-sm border-zinc-200 dark:border-zinc-800 focus-visible:ring-indigo-500/20"
                    />
                    <div className="absolute bottom-4 right-4 text-xs text-muted-foreground pointer-events-none bg-white/80 dark:bg-zinc-950/80 px-2 py-1 rounded backdrop-blur-sm">
                        Supported: English, Hindi, Hinglish
                    </div>
                </div>
            </div>

            {/* Smart Limit Feedback */}
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-indigo-50/50 dark:bg-indigo-950/10 p-4 rounded-lg border border-indigo-100 dark:border-indigo-900/20">
                <div className="flex items-start gap-3">
                    <div className="mt-1 bg-indigo-100 dark:bg-indigo-900/50 p-1.5 rounded-full">
                        <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                        <h4 className="text-sm font-medium text-indigo-900 dark:text-indigo-200">
                            AI Output Preview
                        </h4>
                        <p className="text-sm text-indigo-700 dark:text-indigo-400 mt-0.5">
                            Based on your <strong>{selectedPlan} Plan</strong>, this will be generated as <strong>{currentLimit.pages} pages</strong>.
                        </p>
                    </div>
                </div>
            </div>

            {/* Writing Tips Accordion */}
            <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="tips" className="border-none">
                    <AccordionTrigger className="text-sm text-muted-foreground hover:no-underline py-2">
                        Need help writing a good prompt?
                    </AccordionTrigger>
                    <AccordionContent>
                        <div className="grid sm:grid-cols-2 gap-4 pt-2 pb-4">
                            <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg space-y-2">
                                <h5 className="font-medium text-sm flex items-center gap-2">
                                    <CheckCircle2 className="w-3.5 h-3.5 text-green-500" /> Do
                                </h5>
                                <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                                    <li>Describe the visual style (e.g., &quot;noir&quot;, &quot;watercolor&quot;)</li>
                                    <li>Mention specific character details</li>
                                    <li>Break down complex actions</li>
                                </ul>
                            </div>
                            <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg space-y-2">
                                <h5 className="font-medium text-sm flex items-center gap-2">
                                    <Info className="w-3.5 h-3.5 text-blue-500" /> Tip
                                </h5>
                                <p className="text-xs text-muted-foreground">
                                    You can manually specify panels by writing &quot;Panel 1: [description]&quot; if you want strict control.
                                </p>
                            </div>
                        </div>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
        </div>
    );
}
