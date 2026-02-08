import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Wand2, Zap, Palette, Layers } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-24 pb-32 md:pt-32">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-background z-0" />
        <div className="container px-4 md:px-6 relative z-10 flex flex-col items-center text-center space-y-8">
          <Badge variant="premium" className="px-4 py-1 text-sm rounded-full animate-in fade-in zoom-in duration-500">
            ✨ The Future of Comic Creation
          </Badge>
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-7xl bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/70 sm:max-w-4xl">
            Turn your stories into <br className="hidden md:block" />
            <span className="text-primary">Stunning Comics</span> with AI
          </h1>
          <p className="mx-auto max-w-[700px] text-muted-foreground text-xl md:text-2xl leading-relaxed">
            Create professional-grade graphic novels in minutes. No drawing skills required. Just pure imagination.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full justify-center pt-8">
            <Button size="lg" variant="premium" className="h-14 px-8 text-lg rounded-full">
              Start Creating Now <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full border-primary/20 hover:bg-primary/5">
              View Showcase
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container px-4 py-24 md:px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-background/60 backdrop-blur border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5 group">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Wand2 className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>AI Generation</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Generate consistent characters and scenes with state-of-the-art AI models.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="bg-background/60 backdrop-blur border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5 group">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Palette className="h-6 w-6 text-blue-500" />
              </div>
              <CardTitle>Smart Styling</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Choose from premium presets: Manga, Noir, Western, and Cyberpunk.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="bg-background/60 backdrop-blur border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5 group">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Layers className="h-6 w-6 text-purple-500" />
              </div>
              <CardTitle>Panel Layouts</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Drag-and-drop panel organization with intelligent auto-arranging.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="bg-background/60 backdrop-blur border-primary/10 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5 group">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Zap className="h-6 w-6 text-amber-500" />
              </div>
              <CardTitle>Instant Export</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Export your comics to PDF, CBZ, or web-ready formats instantly.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
