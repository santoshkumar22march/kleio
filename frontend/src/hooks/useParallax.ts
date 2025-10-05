import { useEffect, useRef, useState } from "react";

export function useParallax(speed: number = 0.15, min: number = -120, max: number = 120) {
  const [offset, setOffset] = useState(0);
  const ticking = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const onScroll = () => {
      if (ticking.current) return;
      ticking.current = true;
      requestAnimationFrame(() => {
        const y = window.scrollY * speed;
        const clamped = Math.max(min, Math.min(max, y));
        setOffset(clamped);
        ticking.current = false;
      });
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [speed, min, max]);

  return { style: { ["--parallax-y" as any]: `${offset}px` } as React.CSSProperties };
}
