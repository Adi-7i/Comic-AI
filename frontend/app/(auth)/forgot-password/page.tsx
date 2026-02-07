"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { AuthCard } from "@/components/auth/auth-card"
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/lib/schemas/auth"

export default function ForgotPasswordPage() {
    const [isLoading, setIsLoading] = useState(false)
    const [isSubmitted, setIsSubmitted] = useState(false)

    const form = useForm<ForgotPasswordFormValues>({
        resolver: zodResolver(forgotPasswordSchema),
        defaultValues: {
            email: "",
        },
    })

    async function onSubmit() {
        setIsLoading(true)

        await new Promise((resolve) => setTimeout(resolve, 1000))

        toast.success("Reset link sent!", {
            description: "If an account exists, you will receive an email.",
        })
        setIsSubmitted(true)
        setIsLoading(false)
    }

    if (isSubmitted) {
        return (
            <AuthCard
                title="Check your email"
                description="We have sent a password reset link to your email address."
                footerLink={{
                    text: "Back to login",
                    href: "/login",
                    label: "Did you remember your password?",
                }}
            >
                <div className="flex justify-center">
                    <Button variant="outline" className="w-full" onClick={() => setIsSubmitted(false)}>
                        Try another email
                    </Button>
                </div>
            </AuthCard>
        )
    }

    return (
        <AuthCard
            title="Forgot password?"
            description="Enter your email address and we'll send you a link to reset your password."
        >
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Email</FormLabel>
                                <FormControl>
                                    <Input placeholder="name@example.com" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? "Sending link..." : "Send Reset Link"}
                    </Button>
                    <div className="flex justify-center mt-4">
                        <Link href="/login" className="text-sm text-muted-foreground hover:text-primary flex items-center gap-2 transition-colors">
                            <ArrowLeft className="h-4 w-4" /> Back to login
                        </Link>
                    </div>
                </form>
            </Form>
        </AuthCard>
    )
}
