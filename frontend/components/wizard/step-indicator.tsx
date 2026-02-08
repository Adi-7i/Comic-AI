import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface StepIndicatorProps {
    currentStep: number;
}

export function StepIndicator({ currentStep }: StepIndicatorProps) {
    const steps = [
        { id: 1, label: "Select Plan" },
        { id: 2, label: "Story Input" },
        { id: 3, label: "Scene Preview" },
        { id: 4, label: "Confirmation" },
    ];

    return (
        <div className="w-full mb-8">
            <div className="flex justify-between relative">
                {/* Progress Bar Background */}
                <div className="absolute top-1/2 left-0 w-full h-1 bg-zinc-200 dark:bg-zinc-800 -z-10 -translate-y-1/2 rounded-full" />

                {/* Active Progress Bar */}
                <motion.div
                    className="absolute top-1/2 left-0 h-1 bg-indigo-500 -z-10 -translate-y-1/2 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                />

                {steps.map((step) => {
                    const isActive = currentStep >= step.id;
                    const isCompleted = currentStep > step.id;

                    return (
                        <div key={step.id} className="flex flex-col items-center gap-2 bg-zinc-50 dark:bg-zinc-900 px-2">
                            <motion.div
                                initial={false}
                                animate={{
                                    backgroundColor: isActive ? (isCompleted ? "#6366f1" : "#111827") : "#e4e4e7",
                                    scale: isActive ? 1.1 : 1,
                                    borderColor: isActive ? "#6366f1" : "transparent"
                                }}
                                className={cn(
                                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold border-2 transition-colors duration-300",
                                    isActive ? "text-white border-indigo-500" : "text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400 border-transparent"
                                )}
                            >
                                {isCompleted ? <Check className="w-5 h-5" /> : step.id}
                            </motion.div>
                            <span className={cn(
                                "text-xs font-medium transition-colors duration-300 hidden sm:block",
                                isActive ? "text-indigo-600 dark:text-indigo-400" : "text-zinc-400"
                            )}>
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
