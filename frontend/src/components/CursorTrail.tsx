import React, { useEffect, useState } from "react";

interface Point { id: number; x: number; y: number; }

export const CursorTrail: React.FC = () => {
  const [trail, setTrail] = useState<Point[]>([]);

  useEffect(() => {
    const move = (e: MouseEvent) => {
      setTrail((prev) => {
        const next = [...prev, { id: Date.now() + Math.random(), x: e.clientX, y: e.clientY }];
        return next.slice(-24);
      });
    };
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-[60]">
      {trail.map((p, i) => (
        <div
          key={p.id}
          className="absolute w-2 h-2 rounded-full bg-secondary opacity-50"
          style={{ left: p.x, top: p.y, opacity: i / trail.length, transform: `translate(-50%, -50%) scale(${i / trail.length})` }}
        />
      ))}
    </div>
  );
};
