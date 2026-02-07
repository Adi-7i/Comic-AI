"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/store/auth-store"

export default function ProtectedLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
    const [isMounted, setIsMounted] = useState(false)

    useEffect(() => {
        setIsMounted(true)
    }, [])

    useEffect(() => {
        if (isMounted && !isAuthenticated) {
            router.push("/login")
        }
    }, [isAuthenticated, isMounted, router])

    // Prevent flash of protected content
    if (!isMounted || !isAuthenticated) {
        return null
    }

    return (
        <div className="flex min-h-screen flex-col">
            {/* Re-use main navbar but we could eventually make a dashboard-specific one */}
            <div className="flex-1 space-y-4 p-8 pt-6">
                {children}
            </div>
        </div>
    )
}
