"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { ProgressView } from "./progress-view";
import { SuccessView } from "./success-view";
import { ErrorView } from "./error-view";
import { useEffect } from "react";

export function GenerationView() {
    const { generationStatus, setGenerationStatus, progress, setProgress, setGenerationStep } = useWizardStore();

    // Simulation Logic
    useEffect(() => {
        if (generationStatus === "processing") {
            let currentProgress = progress; // Use store progress
            const interval = setInterval(() => {
                currentProgress += Math.random() * 5;
                if (currentProgress > 100) currentProgress = 100;

                setProgress(currentProgress);

                // Update steps based on progress
                if (currentProgress < 20) setGenerationStep("parsing");
                else if (currentProgress < 50) setGenerationStep("scenes");
                else if (currentProgress < 85) setGenerationStep("generating");
                else setGenerationStep("finalizing");

                if (currentProgress >= 100) {
                    clearInterval(interval);
                    setTimeout(() => {
                        // Randomly fail for testing? No, users hate that. Success!
                        setGenerationStatus("success");
                    }, 1000);
                }
            }, 500);

            const handleBeforeUnload = (e: BeforeUnloadEvent) => {
                e.preventDefault();
                e.returnValue = ""; // Standard for Chrome
                return "";
            };

            window.addEventListener("beforeunload", handleBeforeUnload);

            return () => {
                clearInterval(interval);
                window.removeEventListener("beforeunload", handleBeforeUnload);
            };
        }
    }, [generationStatus, setProgress, setGenerationStep, setGenerationStatus, progress]);

    return (
        <>
            <div className="w-full h-full flex items-center justify-center bg-background/80 backdrop-blur-sm fixed inset-0 z-50">
                <div className="bg-white dark:bg-zinc-900 w-full max-w-2xl rounded-xl shadow-2xl border border-zinc-200 dark:border-zinc-800 m-4 overflow-hidden relative">
                    {generationStatus === "processing" && <ProgressView />}
                    {generationStatus === "success" && <SuccessView />}
                    {generationStatus === "failed" && <ErrorView />}
                </div>
            </div>
        </>
    );
}
