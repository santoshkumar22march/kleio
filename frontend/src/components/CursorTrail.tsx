import React, { useEffect, useRef } from "react";
import { useIsMobile } from "@/hooks/use-mobile";

export const CursorTrail: React.FC = () => {
  const isMobile = useIsMobile();
  const dotRef = useRef<HTMLDivElement | null>(null);
  const glowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Respect reduced motion and mobile devices
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (isMobile || prefersReduced) return;

    let targetX = 0;
    let targetY = 0;
    let dotX = 0;
    let dotY = 0;
    let glowX = 0;
    let glowY = 0;
    let rafId: number | null = null;
    let hideTimeout: number | null = null;

    const show = () => {
      if (dotRef.current) dotRef.current.style.opacity = "1";
      if (glowRef.current) glowRef.current.style.opacity = "0.6";
    };

    const hide = () => {
      if (dotRef.current) dotRef.current.style.opacity = "0";
      if (glowRef.current) glowRef.current.style.opacity = "0";
    };

    const onMove = (e: MouseEvent) => {
      targetX = e.clientX;
      targetY = e.clientY;
      show();
      if (hideTimeout) window.clearTimeout(hideTimeout);
      hideTimeout = window.setTimeout(hide, 900);
      if (rafId == null) rafId = requestAnimationFrame(tick);
    };

    const tick = () => {
      // Lerp factors tuned for snappy dot and softer glow
      dotX += (targetX - dotX) * 0.35;
      dotY += (targetY - dotY) * 0.35;
      glowX += (targetX - glowX) * 0.12;
      glowY += (targetY - glowY) * 0.12;

      if (dotRef.current) {
        dotRef.current.style.left = `${dotX}px`;
        dotRef.current.style.top = `${dotY}px`;
      }
      if (glowRef.current) {
        glowRef.current.style.left = `${glowX}px`;
        glowRef.current.style.top = `${glowY}px`;
      }

      const dx = Math.abs(targetX - dotX);
      const dy = Math.abs(targetY - dotY);
      if (dx > 0.1 || dy > 0.1) {
        rafId = requestAnimationFrame(tick);
      } else {
        rafId = null;
      }
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseenter", show);
    window.addEventListener("mouseleave", hide);

    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseenter", show);
      window.removeEventListener("mouseleave", hide);
      if (rafId != null) cancelAnimationFrame(rafId);
      if (hideTimeout) window.clearTimeout(hideTimeout);
    };
  }, [isMobile]);

  if (isMobile) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-[60]">
      {/* Core dot */}
      <div
        ref={dotRef}
        className="absolute -translate-x-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-primary ring-2 ring-white/70 dark:ring-black/40 shadow-strong transition-opacity duration-200"
        style={{ opacity: 0 }}
      />
      {/* Soft glow */}
      <div
        ref={glowRef}
        className="absolute -translate-x-1/2 -translate-y-1/2 h-16 w-16 rounded-full bg-primary/25 blur-2xl transition-opacity duration-300"
        style={{ opacity: 0 }}
      />
    </div>
  );
};
