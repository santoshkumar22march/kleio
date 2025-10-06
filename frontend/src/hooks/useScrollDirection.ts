import { useEffect, useRef, useState } from "react";

export type ScrollDirection = "up" | "down" | "none";

export function useScrollDirection(threshold: number = 6): ScrollDirection {
  const [dir, setDir] = useState<ScrollDirection>("none");
  const lastY = useRef(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const onScroll = () => {
      const y = window.scrollY;
      const delta = y - lastY.current;
      if (Math.abs(delta) > threshold) {
        setDir(delta > 0 ? "down" : "up");
        lastY.current = y;
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);

  return dir;
}
