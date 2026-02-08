import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useWizardStore } from "@/lib/store/wizard-store";
import { Check, ArrowRight, LayoutDashboard } from "lucide-react";
import Link from "next/link";
import confetti from "canvas-confetti";
import { useEffect } from "react";

export function SuccessView() {
    const { resetWizard } = useWizardStore();

    useEffect(() => {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }, []);

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] max-w-lg mx-auto p-4 text-center">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="w-24 h-24 bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mb-6 ring-8 ring-green-50 dark:ring-green-900/10"
            >
                <Check className="w-12 h-12" />
            </motion.div>

            <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
            >
                <h2 className="text-3xl font-bold mb-2">Your comic is ready!</h2>
                <p className="text-muted-foreground mb-8">
                    &quot;The Galactic Adventures of Robo-Cat&quot; has been successfully generated.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button
                        size="lg"
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 shadow-lg shadow-indigo-500/25"
                    >
                        View Comic <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                    <Link href="/dashboard">
                        <Button variant="outline" size="lg" onClick={resetWizard}>
                            <LayoutDashboard className="w-4 h-4 mr-2" /> Go to Dashboard
                        </Button>
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
