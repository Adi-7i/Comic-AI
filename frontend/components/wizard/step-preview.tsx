import { useWizardStore } from "@/lib/store/wizard-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Image as ImageIcon, Edit2, CheckCircle2 } from "lucide-react";

export function ScenePreview() {
    const { generatedScenes, setStep } = useWizardStore();

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Generated Panels ({generatedScenes.length})</h3>
                <Badge variant="outline" className="border-indigo-500 text-indigo-500">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> AI Optimized
                </Badge>
            </div>

            <ScrollArea className="h-[400px] pr-4">
                <div className="grid gap-4 md:grid-cols-2">
                    {generatedScenes.map((scene, index) => (
                        <Card key={index} className="border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                            <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    Panel {scene.panelNumber}
                                </CardTitle>
                                <Button variant="ghost" size="icon" className="h-6 w-6">
                                    <Edit2 className="w-3 h-3" />
                                </Button>
                            </CardHeader>
                            <CardContent className="p-4 pt-2">
                                <div className="bg-background rounded-md p-3 border text-sm text-zinc-700 dark:text-zinc-300 min-h-[80px]">
                                    {scene.description}
                                </div>
                                <div className="mt-3 flex items-center justify-center h-32 bg-zinc-100 dark:bg-zinc-800 rounded-md border border-dashed border-zinc-300 dark:border-zinc-700">
                                    <div className="flex flex-col items-center text-muted-foreground/50">
                                        <ImageIcon className="w-8 h-8 mb-1" />
                                        <span className="text-xs">Preview Placeholder</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </ScrollArea>

            <div className="flex justify-end pt-4 border-t">
                <Button
                    onClick={() => setStep(4)}
                    className="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-500 text-white"
                >
                    Confirm & Generate Comic
                </Button>
            </div>
        </div>
    );
}
