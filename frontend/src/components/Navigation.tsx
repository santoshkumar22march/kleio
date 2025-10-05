import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "@/components/ui/sonner";

export const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const activeHash = location.hash || "";

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-primary">
              Kleio.ai
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#features"
              className={`nav-link text-sm font-medium ${activeHash === '#features' ? 'text-primary' : 'text-foreground'}`}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className={`nav-link text-sm font-medium ${activeHash === '#how-it-works' ? 'text-primary' : 'text-foreground'}`}
            >
              How It Works
            </a>
            <a
              href="#benefits"
              className={`nav-link text-sm font-medium ${activeHash === '#benefits' ? 'text-primary' : 'text-foreground'}`}
            >
              Benefits
            </a>
          </div>

          {/* CTA Button */}
          <Button
            variant="hero"
            size="sm"
            className="shadow-soft"
            onClick={() => {
              toast.success('Welcome! Taking you to early access...');
              navigate('/signup');
            }}
          >
            Get Early Access
          </Button>
        </div>
      </div>
    </nav>
  );
};
