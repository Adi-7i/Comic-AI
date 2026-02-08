import Header from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";

export default function ProtectedLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex h-screen overflow-hidden bg-zinc-50 dark:bg-zinc-900">
            {/* Desktop Sidebar */}
            <aside className="hidden md:flex w-72 flex-col fixed inset-y-0 z-50">
                <Sidebar />
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 md:ml-72 flex flex-col h-full overflow-hidden">
                <Header />
                <div className="flex-1 overflow-y-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
