"use client"

import * as React from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { Sparkles } from "lucide-react"

interface AuthCardProps extends React.PropsWithChildren {
    title: string
    description: string
    footerLink?: {
        text: string
        href: string
        label: string
    }
    className?: string
}

export function AuthCard({ title, description, children, footerLink, className }: AuthCardProps) {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen px-4 py-12 sm:px-6 lg:px-8">
            <Link href="/" className="mb-8 flex items-center gap-2 group">
                <div className="bg-primary/10 p-2 rounded-lg group-hover:bg-primary/20 transition-colors">
                    <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <span className="font-bold text-2xl tracking-tight">MyComic AI</span>
            </Link>
            <Card className={cn("w-full max-w-md border-primary/10 shadow-xl shadow-primary/5 bg-background/60 backdrop-blur-xl", className)}>
                <CardHeader className="space-y-1 text-center">
                    <CardTitle className="text-2xl font-bold tracking-tight">{title}</CardTitle>
                    <CardDescription>{description}</CardDescription>
                </CardHeader>
                <CardContent>
                    {children}
                </CardContent>
                {footerLink && (
                    <CardFooter className="flex justify-center border-t p-6">
                        <p className="text-sm text-muted-foreground">
                            {footerLink.label}{" "}
                            <Link href={footerLink.href} className="text-primary hover:underline font-medium transition-colors">
                                {footerLink.text}
                            </Link>
                        </p>
                    </CardFooter>
                )}
            </Card>
        </div>
    )
}
