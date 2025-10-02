import { Sparkles } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-muted/30 border-t border-border/50 py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-hero bg-clip-text text-transparent">
                Kleio.ai
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered household intelligence for Indian families. Smarter shopping, better planning, happier homes.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h4 className="font-semibold">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#features" className="hover:text-primary transition-smooth">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-primary transition-smooth">How It Works</a></li>
              <li><a href="#pricing" className="hover:text-primary transition-smooth">Pricing</a></li>
              <li><a href="#faq" className="hover:text-primary transition-smooth">FAQ</a></li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h4 className="font-semibold">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#about" className="hover:text-primary transition-smooth">About Us</a></li>
              <li><a href="#blog" className="hover:text-primary transition-smooth">Blog</a></li>
              <li><a href="#careers" className="hover:text-primary transition-smooth">Careers</a></li>
              <li><a href="#contact" className="hover:text-primary transition-smooth">Contact</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h4 className="font-semibold">Legal</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#privacy" className="hover:text-primary transition-smooth">Privacy Policy</a></li>
              <li><a href="#terms" className="hover:text-primary transition-smooth">Terms of Service</a></li>
              <li><a href="#security" className="hover:text-primary transition-smooth">Security</a></li>
              <li><a href="#cookies" className="hover:text-primary transition-smooth">Cookie Policy</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-border/50 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>© 2025 Kleio.ai. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a href="#twitter" className="hover:text-primary transition-smooth">Twitter</a>
            <a href="#linkedin" className="hover:text-primary transition-smooth">LinkedIn</a>
            <a href="#instagram" className="hover:text-primary transition-smooth">Instagram</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
