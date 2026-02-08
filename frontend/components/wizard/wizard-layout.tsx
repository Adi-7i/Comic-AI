"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { StepIndicator } from "./step-indicator";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface WizardLayoutProps {
    children: React.ReactNode;
    title: string;
    description: string;
}

export function WizardLayout({ children, title, description }: WizardLayoutProps) {
    const { currentStep, setStep } = useWizardStore();

    const handleBack = () => {
        if (currentStep > 1) {
            setStep((currentStep - 1) as 1 | 2 | 3 | 4);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="mb-8 text-center">
                <h1 className="text-3xl font-bold tracking-tight mb-2">{title}</h1>
                <p className="text-muted-foreground">{description}</p>
            </div>

            <StepIndicator currentStep={currentStep} />

            <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm p-6 md:p-8 min-h-[400px]">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                    >
                        {children}
                    </motion.div>
                </AnimatePresence>
            </div>

            <div className="mt-6 flex justify-between">
                <Button
                    variant="ghost"
                    onClick={handleBack}
                    disabled={currentStep === 1}
                    className={currentStep === 1 ? "invisible" : ""}
                >
                    <ArrowLeft className="w-4 h-4 mr-2" /> Back
                </Button>
            </div>
        </div>
    );
}
