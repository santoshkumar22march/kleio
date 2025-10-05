import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { toast } from "@/components/ui/sonner";
import { useParallax } from "@/hooks/useParallax";
import heroImage from "@/assets/hero-kitchen.jpg";

export const Hero = () => {
  const navigate = useNavigate();
  
  const p1 = useParallax(0.12);
  const p2 = useParallax(-0.08);
  const p3 = useParallax(0.06);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 gradient-hero opacity-10" />

      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="parallax absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-float" style={p1.style} />
        <div className="parallax absolute bottom-20 right-10 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float anim-delay-1000" style={p2.style} />
        <div className="parallax absolute -top-24 right-1/3 w-[28rem] h-[28rem] gradient-accent opacity-[0.08] rounded-full blur-3xl animate-float anim-delay-2000" style={p3.style} />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full border border-primary/20">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary">AI-Powered Intelligence</span>
            </div>

            <h1 className="text-5xl lg:text-7xl font-bold leading-tight text-foreground">
              Your Home,
              <br />
              <span className="text-primary">Smarter Every Day</span>
            </h1>

            <p className="text-xl text-muted-foreground leading-relaxed max-w-xl">
              Kleio.ai understands Indian households. From festival planning to daily groceries, 
              we bring AI intelligence to every aspect of your home management.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                variant="hero"
                size="lg"
                className="group"
                onClick={() => {
                  toast.success('Let’s get you early access ✨');
                  navigate('/signup');
                }}
              >
                Get Early Access
                <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  toast.message('Opening sign in…');
                  navigate('/login');
                }}
              >
                Sign In
              </Button>
            </div>

            {/* Indian Languages Support */}
            <div className="flex flex-wrap items-center gap-3 pt-4">
              <span className="text-sm text-muted-foreground">Available in:</span>
              <div className="flex flex-wrap gap-2">
                {["हिंदी", "தமிழ்", "తెలుగు", "ಕನ್ನಡ", "മലയാളം", "বাংলা", "ગુજરાતી", "मराठी"].map((lang) => (
                  <span key={lang} className="px-2 py-1 bg-primary/5 text-primary text-xs font-medium rounded-md border border-primary/10">
                    {lang}
                  </span>
                ))}
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 pt-8">
              <div className="space-y-1">
                <div className="text-3xl font-bold text-primary">10+</div>
                <div className="text-sm text-muted-foreground">Smart Features</div>
              </div>
              <div className="space-y-1">
                <div className="text-3xl font-bold text-secondary">30%</div>
                <div className="text-sm text-muted-foreground">Cost Savings</div>
              </div>
              <div className="space-y-1">
                <div className="text-3xl font-bold text-accent">5hrs</div>
                <div className="text-sm text-muted-foreground">Time Saved/Week</div>
              </div>
            </div>
          </div>

          {/* Right Image */}
          <div className="relative animate-scale-in anim-delay-200 parallax" style={useParallax(0.04).style}>
            <div className="relative rounded-3xl overflow-hidden shadow-strong">
              <img 
                src={heroImage} 
                alt="AI-powered household management with Kleio.ai showing smart kitchen interface"
                className="w-full h-auto object-cover"
              />
              {/* Overlay gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-background/20 to-transparent" />
            </div>
            
            {/* Floating cards */}
            <div className="absolute -top-6 -right-6 bg-card p-4 rounded-2xl shadow-strong border border-border animate-float">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <div className="font-semibold">Festival Alert</div>
                  <div className="text-sm text-muted-foreground">Diwali in 5 days</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
