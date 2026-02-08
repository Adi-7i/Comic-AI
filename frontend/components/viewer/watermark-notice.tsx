import { PlanType } from "@/lib/store/wizard-store";
import { Info } from "lucide-react";

interface WatermarkNoticeProps {
    plan: PlanType;
}

export function WatermarkNotice({ plan }: WatermarkNoticeProps) {
    if (plan === "Creative") return null;

    return (
        <div className="absolute top-4 right-4 z-40 bg-black/50 backdrop-blur-sm text-white px-3 py-1.5 rounded-full text-xs flex items-center gap-1.5 pointer-events-none select-none">
            <Info className="w-3 h-3" />
            <span>Watermark applied ({plan} Plan)</span>
        </div>
    );
}
