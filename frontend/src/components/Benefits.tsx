import { Card, CardContent } from "@/components/ui/card";
import { IndianRupee, Clock, Leaf, Heart } from "lucide-react";

const benefits = [
  {
    icon: IndianRupee,
    title: "₹5,000+ Saved Monthly",
    description: "Smart shopping, bulk buying, and waste reduction translate to real savings",
    stat: "30% Cost Reduction",
    color: "text-primary",
    gradient: "from-primary/20 to-primary/5",
  },
  {
    icon: Clock,
    title: "5 Hours Back Each Week",
    description: "Stop planning, list-making, and market research. Focus on your family instead",
    stat: "60% Time Saved",
    color: "text-secondary",
    gradient: "from-secondary/20 to-secondary/5",
  },
  {
    icon: Leaf,
    title: "40% Less Food Waste",
    description: "Smart consumption tracking and recipe suggestions mean fresh food gets used",
    stat: "Eco-Friendly Living",
    color: "text-accent",
    gradient: "from-accent/20 to-accent/5",
  },
  {
    icon: Heart,
    title: "Peace of Mind",
    description: "Medicine tracking, emergency prep, and festival planning - all handled",
    stat: "Stress-Free Home",
    color: "text-primary",
    gradient: "from-primary/20 to-primary/5",
  },
];

export const Benefits = () => {
  return (
    <section className="py-24 bg-gradient-to-br from-teal-500/5 to-purple-500/5">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4 animate-fade-in">
          <h2 className="text-4xl lg:text-5xl font-bold">
            <span className="bg-gradient-to-r from-primary to-emerald-500 bg-clip-text text-transparent">Real Impact</span>
            <span className="text-foreground">, Measured Results</span>
          </h2>
          <p className="text-xl text-slate-600">
            Join thousands of Indian families already transforming their households
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {benefits.map((benefit, index) => (
            <Card
              key={index}
              className="group backdrop-blur-xl bg-white/60 border border-teal-100 rounded-3xl hover:shadow-2xl hover:shadow-teal-500/10 hover:border-teal-300 transition-all duration-500 animate-scale-in overflow-hidden"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`h-2 bg-gradient-to-r ${benefit.gradient}`} />
              <CardContent className="p-8 space-y-5">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500/20 to-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-smooth">
                  <benefit.icon className={`w-7 h-7 ${benefit.color}`} />
                </div>

                <div className="space-y-2">
                  <div className={`text-lg font-semibold ${benefit.color}`}>
                    {benefit.stat}
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900">{benefit.title}</h3>
                  <p className="text-slate-600 leading-relaxed">
                    {benefit.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
