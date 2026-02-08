import { useWizardStore } from "@/lib/store/wizard-store";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Check, Rocket, AlertTriangle } from "lucide-react";

export function Confirmation() {
    const { selectedPlan, generatedScenes, setGenerationStatus } = useWizardStore();

    const handleStartGeneration = () => {
        setGenerationStatus("processing");
    };

    return (
        <div className="space-y-6 max-w-2xl mx-auto text-center">
            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mx-auto mb-6 ring-8 ring-green-50 dark:ring-green-900/10">
                <Check className="w-10 h-10" />
            </div>

            <h2 className="text-2xl font-bold">Ready to Create Magic?</h2>
            <p className="text-muted-foreground">
                We are about to generate your comic based on the <strong>{selectedPlan} Plan</strong> specifications.
            </p>

            <Card className="text-left border-zinc-200 dark:border-zinc-800 bg-zinc-50/30">
                <CardHeader>
                    <CardTitle className="text-base">Generation Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex justify-between py-2 border-b border-dashed">
                        <span className="text-muted-foreground">Selected Plan</span>
                        <span className="font-medium text-indigo-500">{selectedPlan} Plan</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-dashed">
                        <span className="text-muted-foreground">Total Panels</span>
                        <span className="font-medium">{generatedScenes.length} Panels</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-dashed">
                        <span className="text-muted-foreground">Estimated Time</span>
                        <span className="font-medium">~45 Seconds</span>
                    </div>
                </CardContent>
            </Card>

            {selectedPlan === "Free" && (
                <Alert variant="destructive" className="bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-900 text-left">
                    <AlertTriangle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                    <AlertTitle className="text-orange-800 dark:text-orange-300">Free Plan Limitation</AlertTitle>
                    <AlertDescription className="text-orange-700 dark:text-orange-400/80">
                        You have 1 free comic credit remaining. This action will consume it.
                    </AlertDescription>
                </Alert>
            )}

            <div className="pt-6">
                <Button
                    size="lg"
                    className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 shadow-lg shadow-indigo-500/25"
                    onClick={handleStartGeneration}
                >
                    <Rocket className="w-5 h-5 mr-2" /> Start Generation
                </Button>
                <p className="text-xs text-muted-foreground mt-4">
                    By clicking &quot;Start Generation&quot;, you agree to our Terms of Service.
                </p>
            </div>
        </div>
    );
}
