import { Smartphone, Brain, ShoppingBag, Check } from "lucide-react";

const steps = [
  {
    icon: Smartphone,
    title: "Connect Your Way",
    description: "WhatsApp, voice in Hindi/Tamil/Bengali, photos, or manual entry. Choose what works for you.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: Brain,
    title: "AI Learns Your Family",
    description: "Understands preferences, festivals, dietary needs, and shopping patterns automatically.",
    color: "bg-secondary/10 text-secondary",
  },
  {
    icon: ShoppingBag,
    title: "Smart Suggestions",
    description: "Get personalized shopping lists, recipe ideas, and price alerts tailored to your household.",
    color: "bg-accent/10 text-accent",
  },
  {
    icon: Check,
    title: "Live Smarter",
    description: "Save time, reduce waste, cut costs. More time for what matters - your family.",
    color: "bg-primary/10 text-primary",
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-accent/5 rounded-full blur-3xl -translate-y-1/2" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4 animate-fade-in">
          <h2 className="text-4xl lg:text-5xl font-bold text-foreground">
            Getting Started Is
            <span className="text-accent"> Effortless</span>
          </h2>
          <p className="text-xl text-muted-foreground">
            Four simple steps to transform your household management
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          {steps.map((step, index) => (
            <div 
              key={index} 
              className="relative animate-fade-in-up"
              style={{ animationDelay: `${index * 0.15}s` }}
            >
              {/* Step number */}
              <div className="absolute -top-4 -left-4 w-12 h-12 rounded-full gradient-hero flex items-center justify-center text-white font-bold text-xl shadow-medium">
                {index + 1}
              </div>

              <div className="backdrop-blur-xl bg-white/80 border border-teal-100 rounded-3xl p-8 shadow-lg hover:shadow-2xl hover:shadow-teal-500/10 transition-all duration-500 h-full space-y-4">
                <div className={`w-16 h-16 rounded-2xl ${step.color} flex items-center justify-center`}>
                  <step.icon className="w-8 h-8" />
                </div>

                <h3 className="text-xl font-semibold text-slate-900">{step.title}</h3>
                <p className="text-slate-600 leading-relaxed">{step.description}</p>
              </div>

              {/* Connector line (except for last item) */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-primary/30 to-transparent" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
