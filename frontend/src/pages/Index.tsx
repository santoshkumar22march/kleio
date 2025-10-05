import { useEffect, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { Benefits } from "@/components/Benefits";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";
import { Skeleton } from "@/components/ui/skeleton";
import { Reveal } from "@/components/Reveal";

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
            <Reveal as="section" id="features" className="container mx-auto px-4">
              <Features />
            </Reveal>
            <Reveal as="section" id="how-it-works" className="container mx-auto px-4">
              <HowItWorks />
            </Reveal>
            <Reveal as="section" id="benefits" className="container mx-auto px-4">
              <Benefits />
            </Reveal>
            <Reveal>
              <CTA />
            </Reveal>
          </>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default Index;
