import { Calendar, Users, MessageSquare, TrendingDown, Brain, Leaf, ShoppingCart, Bell, Heart, Shield } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Calendar,
    title: "Festival Intelligence",
    description: "Automatic shopping lists for Diwali, Holi, Eid, Christmas. Knows your traditions.",
    color: "text-primary",
  },
  {
    icon: Users,
    title: "Multi-Gen Family Care",
    description: "Track dietary needs from diabetic grandparents to school-going kids.",
    color: "text-secondary",
  },
  {
    icon: MessageSquare,
    title: "WhatsApp Integration",
    description: "Simply text 'bought 2kg tomatoes' - inventory updated instantly.",
    color: "text-accent",
  },
  {
    icon: Brain,
    title: "AI Meal Planning",
    description: "Generate recipes from what's in your kitchen. Zero waste, maximum taste.",
    color: "text-secondary",
  },
  {
    icon: ShoppingCart,
    title: "Smart Shopping",
    description: "Predict needs based on school calendar, cook's schedule, and weather.",
    color: "text-accent",
  },
  {
    icon: Bell,
    title: "Medicine Management",
    description: "Never run out of critical medications. Doctor prescription integration.",
    color: "text-primary",
  },
  {
    icon: Leaf,
    title: "Sustainability First",
    description: "Track plastic footprint. Promote local, seasonal, organic choices.",
    color: "text-accent",
  },
];

export const Features = () => {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4 animate-fade-in">
          <h2 className="text-4xl lg:text-5xl font-bold text-foreground">
            Intelligence That
            <span className="text-primary"> Understands India</span>
          </h2>
          <p className="text-xl text-muted-foreground">
            From festival prep to daily meals, Kleio.ai brings AI power to every corner of your household
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="group hover:shadow-medium transition-smooth border-border/50 animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardContent className="p-6 space-y-4">
                <div className="w-12 h-12 rounded-xl gradient-feature flex items-center justify-center group-hover:scale-110 transition-smooth">
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="font-semibold text-lg leading-tight">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
