"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, AlertCircle, Leaf } from "lucide-react"
import CritiqueResult from "@/components/critique-result"

interface Message {
  id: string
  type: "user" | "coach"
  content: string | CritiqueData
  timestamp: Date
}

interface CritiqueData {
  plan: string[]
  tips: {
    [key: string]: string[]
  }
  feedback: {
    critique: string
    questions: string[]
  }
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    const text = input.trim()
    if (!text) return

    if (text.length < 50) {
      setError("Please provide at least 50 words for a full critique.")
      return
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")

    // Simulate coach response with timeout
    setIsLoading(true)
    setTimeout(() => {
      const critiqueData: CritiqueData = {
        plan: ["Pacing", "Dialogue", "Show-Don't-Tell"],
        tips: {
          Pacing: [
            "Vary sentence length to control rhythm",
            "Use short sentences for impact",
            "Balance action with reflection",
          ],
          Dialogue: [
            "Make dialogue reveal character, not just information",
            "Use dialogue tags sparingly",
            "Avoid exposition in conversation",
          ],
          "Show-Don't-Tell": [
            "Replace emotional statements with sensory details",
            "Let actions and dialogue convey meaning",
            "Trust the reader to interpret",
          ],
        },
        feedback: {
          critique:
            "Your piece shows strong voice and clear intent. The opening draws readers in effectively. Consider varying your sentence structure more—several consecutive long sentences slow the pacing in the middle section. Your dialogue feels natural, though one exchange could be tightened to increase tension.",
          questions: [
            "What emotional response do you want from readers at the climax?",
            "Are there moments where you're telling instead of showing the character's state of mind?",
            "Which scene felt most challenging to write, and why?",
          ],
        },
      }

      const coachMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "coach",
        content: critiqueData,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, coachMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleReset = () => {
    setMessages([])
    setError(null)
    setInput("")
  }

  return (
    <div className="flex flex-col h-screen bg-black">
      {/* Header */}
      <div className="border-b border-green-500/20 glass-hover bg-black/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-500/10 border border-green-500/30">
              <Leaf className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-green-400">Project Forge</h1>
              <p className="text-xs text-green-400/60">Local-first writing coach</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-green-400/70 hover:text-green-400 hover:bg-green-500/10 rounded-lg transition-colors"
            >
              New Chat
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-96 text-center">
              <div className="p-4 rounded-xl glass mb-6">
                <Leaf className="w-12 h-12 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Ready to improve your writing?</h2>
              <p className="text-white/60 max-w-sm">
                Paste your draft below and get actionable critique from your AI writing coach. Minimum 50 words.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div key={message.id} className={`mb-6 ${message.type === "user" ? "text-right" : "text-left"}`}>
                  {message.type === "user" ? (
                    <div className="inline-block max-w-2xl">
                      <div className="glass rounded-2xl px-6 py-4 text-left bg-green-500/10 border-green-500/30">
                        <p className="text-white/90">{message.content}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="max-w-3xl">
                      <CritiqueResult data={message.content as CritiqueData} />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-green-500/20 glass-hover bg-black/80 backdrop-blur-sm sticky bottom-0">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {error && (
            <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex gap-3 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste your writing here (minimum 50 words for full critique)..."
              className="w-full px-4 py-4 bg-black border border-green-500/30 rounded-xl text-white placeholder:text-white/40 focus:outline-none focus:border-green-400/60 focus:ring-2 focus:ring-green-500/20 resize-none"
              rows={4}
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-green-400/70">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span>Processing locally • No data stored</span>
              </div>

              <button
                type="submit"
                disabled={isLoading || input.trim().length < 50}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-black rounded-lg font-semibold hover:shadow-[0_0_20px_rgba(34,197,94,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 rounded-full border-2 border-black/30 border-t-black animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Get Critique
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
