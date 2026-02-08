import { Button } from "@/components/ui/button";
import { useViewerStore } from "@/lib/store/viewer-store";
import { ChevronLeft, ChevronRight, LayoutTemplate, Minimize2 } from "lucide-react";
import { motion } from "framer-motion";

export function ViewerControls() {
    const {
        currentPage,
        totalPages,
        nextPage,
        prevPage,
        isDistractionFree,
        toggleDistractionFree
    } = useViewerStore();

    if (isDistractionFree) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 left-0 right-0 flex justify-center items-center z-50 pointer-events-none"
        >
            <div className="bg-white/90 dark:bg-zinc-800/90 backdrop-blur-md px-4 py-2 rounded-full shadow-2xl border border-zinc-200 dark:border-zinc-700 flex items-center gap-4 pointer-events-auto">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={prevPage}
                    disabled={currentPage === 1}
                    className="rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700"
                >
                    <ChevronLeft className="w-5 h-5" />
                </Button>

                <div className="text-sm font-medium tabular-nums min-w-[80px] text-center">
                    Page {currentPage} of {totalPages}
                </div>

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={nextPage}
                    disabled={currentPage === totalPages}
                    className="rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700"
                >
                    <ChevronRight className="w-5 h-5" />
                </Button>

                <div className="w-px h-6 bg-zinc-200 dark:bg-zinc-700 mx-2" />

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleDistractionFree}
                    className="rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700"
                    title="Distraction Free Mode"
                >
                    {isDistractionFree ? <Minimize2 className="w-4 h-4" /> : <LayoutTemplate className="w-4 h-4" />}
                </Button>
            </div>
        </motion.div>
    );
}
