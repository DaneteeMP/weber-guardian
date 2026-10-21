import { useEffect, useState } from "react";

interface SplashScreenProps {
  onComplete: () => void;
}

// Full-screen brand splash shown only right after the Gate password passes
// (parity with WeberAssistant's SplashScreen.tsx): fade+zoom in (700ms),
// hold, fade+zoom out, done at 2200ms. Pure presentation, no fetches.
export default function SplashScreen({ onComplete }: SplashScreenProps) {
  const [phase, setPhase] = useState<"enter" | "visible" | "exit">("enter");

  useEffect(() => {
    const t1 = setTimeout(() => setPhase("visible"), 50);
    const t2 = setTimeout(() => setPhase("exit"), 1500);
    const t3 = setTimeout(() => onComplete(), 2200);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center" style={{ backgroundColor: "#1D4F91" }}>
      <div
        className="flex flex-col items-center transition-all duration-700 ease-in-out"
        style={{
          opacity: phase === "enter" ? 0 : phase === "visible" ? 1 : 0,
          transform:
            phase === "enter"
              ? "scale(0.8)"
              : phase === "visible"
                ? "scale(1)"
                : "scale(1.1)",
        }}
      >
        <div className="relative mb-4">
          <div className="w-96 h-96 rounded-full bg-white shadow-2xl" />
          <img
            src="/guardian-logo.png"
            alt="Guardian"
            className="w-56 h-auto absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
          />
        </div>
      </div>
    </div>
  );
}
