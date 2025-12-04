"use client"

import { Leaf } from "lucide-react"

interface WelcomeScreenProps {
  onStart: () => void
}

export default function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">
      <div className="relative z-10 text-center max-w-2xl">
        <div className="flex justify-center mb-8">
          <div className="p-4 rounded-2xl glass-card glow-mixed">
            <Leaf className="w-14 h-14 text-green-400" />
          </div>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gradient">Project Forge</h1>

        <p className="text-xl text-white/70 mb-4">Your local-first AI writing coach</p>

        <p className="text-lg text-white/60 mb-12 leading-relaxed">
          Get constructive critique on your writing. Receive questions that spark deeper thinking. Discover techniques
          to strengthen your prose—all processed locally, with complete privacy.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <button
            onClick={onStart}
            className="px-8 py-4 bg-gradient-to-r from-green-500 via-emerald-500 to-cyan-500 text-black rounded-xl font-bold text-lg hover:shadow-[0_0_40px_rgba(34,197,94,0.5),0_0_80px_rgba(6,182,212,0.3)] transition-all duration-300 hover:scale-105"
          >
            Start Writing
          </button>
        </div>

        <div className="flex items-center justify-center gap-2 text-sm text-green-400/70">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>All processing is local and private</span>
        </div>
      </div>
    </div>
  )
}
