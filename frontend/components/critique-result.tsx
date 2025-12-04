import { CheckCircle, MessageCircle } from "lucide-react"

interface CritiqueResultProps {
  data: {
    plan: string[]
    tips: {
      [key: string]: string[]
    }
    feedback: {
      critique: string
      questions: string[]
    }
  }
}

export default function CritiqueResult({ data }: CritiqueResultProps) {
  return (
    <div className="space-y-6">
      {/* Critique Plan */}
      <div className="glass rounded-2xl p-6 border-green-500/30 bg-green-500/5">
        <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          Critique Plan
        </h3>
        <div className="flex gap-2 flex-wrap">
          {data.plan.map((item, idx) => (
            <span
              key={idx}
              className="px-4 py-2 bg-green-500/20 border border-green-400/40 rounded-full text-sm text-green-300 font-medium"
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Writing Tips */}
      <div className="space-y-4">
        {Object.entries(data.tips).map(([dimension, tips]) => (
          <div key={dimension} className="glass rounded-2xl p-6 border-green-500/30">
            <h4 className="text-green-400 font-semibold mb-3">{dimension}</h4>
            <ul className="space-y-2">
              {tips.map((tip, idx) => (
                <li key={idx} className="flex gap-3 text-white/80 text-sm leading-relaxed">
                  <span className="text-green-400 flex-shrink-0 font-bold">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Coach Feedback */}
      <div className="glass rounded-2xl p-6 border-green-500/30 bg-green-500/5">
        <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          Coach Feedback
        </h3>

        <div className="mb-6">
          <p className="text-white/80 leading-relaxed">{data.feedback.critique}</p>
        </div>

        <div>
          <h4 className="text-green-300 font-semibold mb-3">Questions to Consider:</h4>
          <ul className="space-y-2">
            {data.feedback.questions.map((question, idx) => (
              <li key={idx} className="flex gap-3 text-white/70 text-sm leading-relaxed">
                <span className="text-green-400 flex-shrink-0">→</span>
                <span>{question}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
