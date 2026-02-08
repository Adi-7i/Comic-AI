import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useWizardStore } from "@/lib/store/wizard-store";
import { AlertTriangle, RefreshCw, PenTool } from "lucide-react";

export function ErrorView() {
    const { error, setGenerationStatus, setStep } = useWizardStore();

    const handleRetry = () => {
        setGenerationStatus("processing");
        // In a real app, this would re-trigger the generation function
    };

    const handleEdit = () => {
        setGenerationStatus("idle");
        setStep(2); // Go back to story input
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] max-w-lg mx-auto p-4 text-center">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="w-20 h-20 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-full flex items-center justify-center mb-6"
            >
                <AlertTriangle className="w-10 h-10" />
            </motion.div>

            <h2 className="text-2xl font-bold mb-2">Generation Failed</h2>
            <p className="text-muted-foreground mb-8 max-w-sm mx-auto">
                {error || "Something went wrong while creating your comic. Please try again."}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button onClick={handleRetry} className="bg-indigo-600 hover:bg-indigo-700">
                    <RefreshCw className="w-4 h-4 mr-2" /> Retry Generation
                </Button>
                <Button variant="outline" onClick={handleEdit}>
                    <PenTool className="w-4 h-4 mr-2" /> Edit Story
                </Button>
            </div>
        </div>
    );
}
