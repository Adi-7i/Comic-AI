"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { ProgressView } from "./progress-view";
import { SuccessView } from "./success-view";
import { ErrorView } from "./error-view";
import { useEffect } from "react";
import { generationApi } from "@/lib/api/generation";

export function GenerationView() {
    const { generationStatus, setGenerationStatus, setProgress, setGenerationStep } = useWizardStore();

    // Generation Logic
    useEffect(() => {
        if (generationStatus === "processing") {
            let mounted = true;

            const generate = async () => {
                try {
                    // Simulate step updates for delight
                    setGenerationStep("parsing");
                    setProgress(10);
                    await new Promise(r => setTimeout(r, 800));

                    if (!mounted) return;
                    setGenerationStep("scenes");
                    setProgress(40);
                    await new Promise(r => setTimeout(r, 800));

                    if (!mounted) return;
                    setGenerationStep("generating");
                    setProgress(70);

                    // Call API (Mock or Real)
                    await generationApi.generateComic("prompt placeholder", "Pro");

                    if (!mounted) return;
                    setGenerationStep("finalizing");
                    setProgress(100);

                    setTimeout(() => {
                        if (mounted) setGenerationStatus("success");
                    }, 500);

                } catch (err) {
                    console.error("Generation failed", err);
                    if (mounted) {
                        setGenerationStatus("failed");
                        // setError(err.message);
                    }
                }
            };

            generate();

            const handleBeforeUnload = (e: BeforeUnloadEvent) => {
                e.preventDefault();
                e.returnValue = "";
                return "";
            };

            window.addEventListener("beforeunload", handleBeforeUnload);

            return () => {
                mounted = false;
                window.removeEventListener("beforeunload", handleBeforeUnload);
            };
        }
    }, [generationStatus, setProgress, setGenerationStep, setGenerationStatus]);

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
