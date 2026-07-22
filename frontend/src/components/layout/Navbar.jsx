import { Sparkles } from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-16 border-b border-gray-800 bg-gray-950 flex items-center justify-between px-8">
      <div className="flex items-center gap-3">
        <Sparkles className="text-cyan-400" size={28} />
        <h1 className="text-2xl font-bold">
          AutoDev <span className="text-cyan-400">AI</span>
        </h1>
      </div>

      <div className="text-gray-400">
        Autonomous AI Software Engineer
      </div>
    </header>
  );
}