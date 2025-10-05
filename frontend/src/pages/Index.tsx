import { useEffect, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { Benefits } from "@/components/Benefits";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";
import { Skeleton } from "@/components/ui/skeleton";

const Index = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 400);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen">
      <Navigation />
      <main>
        {loading ? (
          <section className="relative min-h-[80vh] flex items-center justify-center">
            <div className="container mx-auto px-4 grid lg:grid-cols-2 gap-12 items-center">
              <div className="space-y-6">
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-16 w-3/4" />
                <Skeleton className="h-16 w-2/3" />
                <Skeleton className="h-6 w-2/3" />
                <div className="flex gap-4">
                  <Skeleton className="h-11 w-40 rounded-lg" />
                  <Skeleton className="h-11 w-28 rounded-lg" />
                </div>
              </div>
              <Skeleton className="h-[380px] w-full rounded-3xl" />
            </div>
          </section>
        ) : (
          <>
            <Hero />
            <section id="features">
              <Features />
            </section>
            <section id="how-it-works">
              <HowItWorks />
            </section>
            <section id="benefits">
              <Benefits />
            </section>
            <CTA />
          </>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default Index;
