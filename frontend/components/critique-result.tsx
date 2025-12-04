import { CheckCircle, MessageCircle, Lightbulb } from "lucide-react"
import MarkdownRenderer from "@/components/markdown-renderer"

interface CritiqueResultProps {
  data: {
    plan: {
      input: string
      classification: string
      dimensions: string[]
    }
    tips: string[]
    critique: string
  }
}

export default function CritiqueResult({ data }: CritiqueResultProps) {
  return (
    <div className="space-y-6">
      {/* Critique Plan */}
      <div className="glass-card rounded-2xl p-6 border-green-500/30 bg-green-500/5">
        <h3 className="text-lg font-semibold text-gradient mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-400" />
          Analysis Dimensions
        </h3>
        <div className="flex gap-2 flex-wrap">
          {data.plan.dimensions.map((item, idx) => (
            <span
              key={idx}
              className="px-4 py-2 bg-gradient-to-r from-green-500/20 to-cyan-500/10 border border-green-400/40 rounded-full text-sm text-green-300 font-medium"
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Writing Tips from RAG */}
      {data.tips && data.tips.length > 0 && (
        <div className="glass-card rounded-2xl p-6 border-cyan-500/30 bg-cyan-500/5">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Writing Tips from Knowledge Base
          </h3>
          <ul className="space-y-3">
            {data.tips.map((tip, idx) => (
              <li key={idx} className="flex gap-3 text-white/80 text-sm leading-relaxed">
                <span className="text-cyan-400 flex-shrink-0 font-bold">•</span>
                <span className="line-clamp-3">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Forge Agent Feedback */}
      <div className="glass-card rounded-2xl p-6 border-green-500/30 bg-green-500/5 glow-mixed">
        <h3 className="text-lg font-semibold text-gradient mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-green-400" />
          Forge Agent
        </h3>

        <MarkdownRenderer>{data.critique}</MarkdownRenderer>
      </div>
    </div>
  )
}
