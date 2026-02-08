import { motion } from "framer-motion";
import { useWizardStore, GenerationStep } from "@/lib/store/wizard-store";
import { Loader2, CheckCircle2, FileText, Image as ImageIcon, Sparkles, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export function ProgressView() {
    const { progress, generationStep } = useWizardStore();

    const steps: { id: GenerationStep; label: string; icon: React.ElementType }[] = [
        { id: "parsing", label: "Analysing your story script...", icon: FileText },
        { id: "scenes", label: "Drafting scene layouts...", icon: ImageIcon },
        { id: "generating", label: "Generating comic panels...", icon: Sparkles },
        { id: "finalizing", label: "Finalizing details...", icon: CheckCircle2 },
    ];

    const getStepStatus = (stepId: GenerationStep, currentStep: GenerationStep) => {
        const stepOrder = ["parsing", "scenes", "generating", "finalizing"];
        const currentIndex = stepOrder.indexOf(currentStep);
        const stepIndex = stepOrder.indexOf(stepId);

        if (stepIndex < currentIndex) return "completed";
        if (stepIndex === currentIndex) return "active";
        return "pending";
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] max-w-lg mx-auto p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-8"
            >
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500 mb-2">
                    Creating your comic...
                </h2>
                <p className="text-muted-foreground">
                    This usually takes about a minute. Please don&apos;t refresh the page.
                </p>
            </motion.div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-8 overflow-hidden">
                <motion.div
                    className="h-full bg-indigo-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: "linear" }}
                />
            </div>

            {/* Steps List */}
            <div className="w-full space-y-4">
                {steps.map((step) => {
                    const status = getStepStatus(step.id, generationStep);
                    const Icon = step.icon;

                    return (
                        <motion.div
                            key={step.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={cn(
                                "flex items-center p-3 rounded-lg border transition-colors",
                                status === "active"
                                    ? "border-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-900/20"
                                    : "border-transparent"
                            )}
                        >
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center mr-4 transition-colors",
                                status === "completed" ? "bg-green-100 dark:bg-green-900/20 text-green-600" :
                                    status === "active" ? "bg-indigo-100 dark:bg-indigo-900/20 text-indigo-600" :
                                        "bg-zinc-100 dark:bg-zinc-800 text-zinc-400"
                            )}>
                                {status === "completed" ? <Check className="w-4 h-4" /> :
                                    status === "active" ? <Loader2 className="w-4 h-4 animate-spin" /> :
                                        <Icon className="w-4 h-4" />}
                            </div>
                            <span className={cn(
                                "text-sm font-medium",
                                status === "pending" && "text-muted-foreground"
                            )}>
                                {step.label}
                            </span>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
