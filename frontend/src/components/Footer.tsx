import { Sparkles } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-teal-500/20 py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-teal-400">
                Kleio.ai
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              AI-powered household intelligence for Indian families. Smarter shopping, better planning, happier homes.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h4 className="font-semibold text-white">Product</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#features" className="hover:text-teal-400 transition-smooth">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-teal-400 transition-smooth">How It Works</a></li>
              <li><a href="#pricing" className="hover:text-teal-400 transition-smooth">Pricing</a></li>
              <li><a href="#faq" className="hover:text-teal-400 transition-smooth">FAQ</a></li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h4 className="font-semibold text-white">Company</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#about" className="hover:text-teal-400 transition-smooth">About Us</a></li>
              <li><a href="#blog" className="hover:text-teal-400 transition-smooth">Blog</a></li>
              <li><a href="#careers" className="hover:text-teal-400 transition-smooth">Careers</a></li>
              <li><a href="#contact" className="hover:text-teal-400 transition-smooth">Contact</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h4 className="font-semibold text-white">Legal</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#privacy" className="hover:text-teal-400 transition-smooth">Privacy Policy</a></li>
              <li><a href="#terms" className="hover:text-teal-400 transition-smooth">Terms of Service</a></li>
              <li><a href="#security" className="hover:text-teal-400 transition-smooth">Security</a></li>
              <li><a href="#cookies" className="hover:text-teal-400 transition-smooth">Cookie Policy</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-teal-500/20 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-400">
          <p>© 2025 Kleio.ai. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a href="#twitter" className="hover:text-teal-400 transition-smooth">Twitter</a>
            <a href="#linkedin" className="hover:text-teal-400 transition-smooth">LinkedIn</a>
            <a href="#instagram" className="hover:text-teal-400 transition-smooth">Instagram</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
