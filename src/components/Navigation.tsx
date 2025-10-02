import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

export const Navigation = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-hero bg-clip-text text-transparent">
              Kleio.ai
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-foreground hover:text-primary transition-smooth">
              Features
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-foreground hover:text-primary transition-smooth">
              How It Works
            </a>
            <a href="#benefits" className="text-sm font-medium text-foreground hover:text-primary transition-smooth">
              Benefits
            </a>
          </div>

          {/* CTA Button */}
          <Button variant="hero" size="sm" className="shadow-soft">
            Get Early Access
          </Button>
        </div>
      </div>
    </nav>
  );
};
