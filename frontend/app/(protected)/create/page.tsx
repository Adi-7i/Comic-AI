"use client";

import { useWizardStore } from "@/lib/store/wizard-store";
import { StudioLayout } from "@/components/create/studio-layout";
import { StoryEditor } from "@/components/create/story-editor";
import { ReviewSection } from "@/components/create/review-section";
import { GenerationView } from "@/components/generation/generation-view";
import { AnimatePresence } from "framer-motion";

export default function CreatePage() {
    const { generationStatus } = useWizardStore();
    const isGenerating = generationStatus !== "idle";

    return (
        <>
            <StudioLayout>
                <div className="max-w-3xl mx-auto space-y-8">
                    <StoryEditor />
                    <ReviewSection />
                </div>
            </StudioLayout>

            {/* Generation Overlay */}
            <AnimatePresence>
                {isGenerating && <GenerationView />}
            </AnimatePresence>
        </>
    );
}
