import { Button } from "@/components/ui/button";
import { useViewerStore } from "@/lib/store/viewer-store";
import { ZoomIn, ZoomOut, Maximize, Minimize } from "lucide-react";
import { motion } from "framer-motion";

export function ZoomControls() {
    const { zoomLevel, setZoom, resetZoom, viewMode, setViewMode } = useViewerStore();

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="fixed right-6 bottom-24 flex flex-col gap-2 bg-white/90 dark:bg-zinc-800/90 backdrop-blur-md p-2 rounded-lg shadow-xl border border-zinc-200 dark:border-zinc-700 z-50"
        >
            <Button
                variant="ghost"
                size="icon"
                onClick={() => setZoom((z) => z + 10)}
                className="h-8 w-8 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700"
                title="Zoom In"
            >
                <ZoomIn className="w-4 h-4" />
            </Button>

            <div className="text-xs font-mono text-center py-1 text-muted-foreground select-none">
                {Math.round(zoomLevel)}%
            </div>

            <Button
                variant="ghost"
                size="icon"
                onClick={() => setZoom((z) => z - 10)}
                className="h-8 w-8 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700"
                title="Zoom Out"
            >
                <ZoomOut className="w-4 h-4" />
            </Button>

            <div className="w-full h-px bg-zinc-200 dark:bg-zinc-700 my-1" />

            <Button
                variant={viewMode === "fit-width" ? "secondary" : "ghost"}
                size="icon"
                onClick={() => setViewMode("fit-width")}
                className="h-8 w-8 rounded-md"
                title="Fit to Width"
            >
                <Maximize className="w-4 h-4" />
            </Button>

            <Button
                variant={viewMode === "fit-screen" ? "secondary" : "ghost"}
                size="icon"
                onClick={() => setViewMode("fit-screen")}
                className="h-8 w-8 rounded-md"
                title="Fit to Screen"
            >
                <Minimize className="w-4 h-4" />
            </Button>
            <Button
                variant="ghost"
                size="icon"
                onClick={resetZoom}
                className="h-8 w-8 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700 text-xs"
                title="Reset"
            >
                Rst
            </Button>
        </motion.div>
    );
}
