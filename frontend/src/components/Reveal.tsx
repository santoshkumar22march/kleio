import React, { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

type RevealProps<E extends keyof JSX.IntrinsicElements = "div"> = {
  as?: E;
  className?: string;
  children: React.ReactNode;
} & JSX.IntrinsicElements[E];

export function Reveal<E extends keyof JSX.IntrinsicElements = "div">({ as, className, children, ...rest }: RevealProps<E>) {
  const Tag = (as || "div") as any;
  const ref = useRef<HTMLDivElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!ref.current) return;
    const el = ref.current;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <Tag ref={ref} className={cn("reveal-up", visible && "reveal-visible", className)} {...(rest as any)}>
      {children}
    </Tag>
  );
}
