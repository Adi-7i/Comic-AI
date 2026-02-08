import { useWizardStore } from "@/lib/store/wizard-store";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Lightbulb, Hash } from "lucide-react";
import { useState } from "react";

export function StoryInput() {
    const { storyText, setStory, setStep, setScenes } = useWizardStore();
    const [isProcessing, setIsProcessing] = useState(false);

    // Mock scene generation logic
    const handlePreviewScenes = () => {
        setIsProcessing(true);

        // Simulate API delay
        setTimeout(() => {
            // Mock data based on story length
            const newScenes = Array.from({ length: 4 }).map((_, i) => ({
                id: `scene-${i}`,
                pageNumber: 1,
                panelNumber: i + 1,
                description: `A scene based on: "${storyText.substring(0, 20)}..."`,
                image: undefined
            }));

            setScenes(newScenes);
            setIsProcessing(false);
            setStep(3);
        }, 1500);
    };

    return (
        <div className="space-y-6">
            <div className="bg-indigo-50 dark:bg-indigo-950/30 p-4 rounded-lg flex items-start gap-3 border border-indigo-100 dark:border-indigo-900/50">
                <Lightbulb className="w-5 h-5 text-indigo-600 dark:text-indigo-400 mt-0.5 shrink-0" />
                <div className="text-sm text-indigo-900 dark:text-indigo-200">
                    <p className="font-medium mb-1">Writing Tips:</p>
                    <ul className="list-disc list-inside space-y-1 opacity-90">
                        <li>Describe the setting and characters clearly.</li>
                        <li>Break down complex actions into multiple sentences.</li>
                        <li>You can specify &quot;Panel 1:&quot;, &quot;Panel 2:&quot; for manual control.</li>
                        <li>English, Hindi, and Hinglish are supported.</li>
                    </ul>
                </div>
            </div>

            <div className="relative">
                <Textarea
                    value={storyText}
                    onChange={(e) => setStory(e.target.value)}
                    placeholder="Once upon a time in a cyber-noir city..."
                    className="min-h-[300px] text-lg resize-none p-4 leading-relaxed focus-visible:ring-indigo-500"
                />
                <div className="absolute bottom-4 right-4 text-xs text-muted-foreground bg-background/80 backdrop-blur px-2 py-1 rounded-md flex items-center border">
                    <Hash className="w-3 h-3 mr-1" />
                    {storyText.length} chars
                </div>
            </div>

            <div className="flex justify-between items-center pt-4">
                <span className="text-sm text-muted-foreground hidden sm:block">
                    {storyText.length > 50 ? "Ready to generate!" : "Minimum 50 characters recommended"}
                </span>
                <Button
                    onClick={handlePreviewScenes}
                    disabled={storyText.length < 50 || isProcessing}
                    className="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-500 text-white min-w-[150px]"
                >
                    {isProcessing ? "Analyzing..." : "Preview Scenes"}
                </Button>
            </div>
        </div>
    );
}
