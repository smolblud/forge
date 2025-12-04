"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, AlertCircle, Leaf } from "lucide-react"
import CritiqueResult from "@/components/critique-result"
import MarkdownRenderer from "@/components/markdown-renderer"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Message {
  id: string
  type: "user" | "coach"
  content: string | CritiqueData
  timestamp: Date
}

interface CritiqueData {
  plan: {
    input: string
    classification: string
    dimensions: string[]
  }
  tips: string[]
  critique: string
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



    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")

    // Call the real API
    setIsLoading(true)
    try {
      const response = await fetch(`${API_URL}/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to get response")
      }

      const result = await response.json()

      let coachMessage: Message
      if (result.critique) {
        // Critique flow
        coachMessage = {
          id: (Date.now() + 1).toString(),
          type: "coach",
          content: {
            plan: result.plan,
            tips: result.tips,
            critique: result.critique,
          },
          timestamp: new Date(),
        }
      } else if (result.response) {
        // Question/short answer flow
        coachMessage = {
          id: (Date.now() + 1).toString(),
          type: "coach",
          content: result.response,
          timestamp: new Date(),
        }
      } else {
        coachMessage = {
          id: (Date.now() + 1).toString(),
          type: "coach",
          content: "No response from coach.",
          timestamp: new Date(),
        }
      }
      setMessages((prev) => [...prev, coachMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to the writing coach. Make sure the backend is running on port 8000.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setMessages([])
    setError(null)
    setInput("")
  }

  return (
    <div className="flex flex-col h-screen bg-transparent relative">
      {/* Header */}
      <div className="border-b border-green-500/20 glass-card sticky top-0 z-20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-green-500/20 to-cyan-500/10 border border-green-500/30 glow-green">
              <Leaf className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">Project Forge</h1>
              <p className="text-xs text-cyan-400/60">Local-first writing coach</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-green-400/70 hover:text-green-400 hover:bg-green-500/10 rounded-lg transition-all duration-300 border border-transparent hover:border-green-500/30"
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
                Paste your writing, ask a question, or submit any text. Get instant critique or advice from your AI writing coach.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div key={message.id} className={`mb-6 ${message.type === "user" ? "text-right" : "text-left"}`}>
                  {message.type === "user" ? (
                    <div className="inline-block max-w-2xl">
                      <div className="glass rounded-2xl px-6 py-4 text-left bg-green-500/10 border-green-500/30">
                        <p className="text-white/90">{typeof message.content === "string" ? message.content : ""}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="max-w-3xl">
                      {typeof message.content === "string" ? (
                        <div className="glass-card rounded-2xl p-6 border-cyan-500/30 bg-cyan-500/5">
                          <h3 className="text-lg font-semibold text-cyan-400 mb-4 flex items-center gap-2">
                            Forge Agent
                          </h3>
                          <MarkdownRenderer>{message.content}</MarkdownRenderer>
                        </div>
                      ) : (
                        <CritiqueResult data={message.content as CritiqueData} />
                      )}
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="mb-6 text-left max-w-3xl">
                  <div className="glass-card rounded-2xl p-6 border-cyan-500/30 bg-cyan-500/5 flex items-center gap-3">
                    <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
                    <span className="text-cyan-400 font-semibold animate-pulse">Forge is thinking<span className="dot-typing ml-1"></span></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-green-500/20 glass-card sticky bottom-0">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {error && (
            <div className="mb-4 p-4 rounded-xl glass-card bg-red-500/10 border border-red-500/30 flex gap-3 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (input.trim().length > 0 && !isLoading) {
                    handleSubmit(e as any);
                  }
                }
              }}
              placeholder="Paste your writing, ask a question, or submit any text..."
              className="w-full px-4 py-4 bg-black/50 border border-green-500/30 rounded-xl text-white placeholder:text-white/40 focus:outline-none focus:border-cyan-400/60 focus:ring-2 focus:ring-cyan-500/20 resize-none transition-all duration-300"
              rows={4}
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-cyan-400/70">
                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                <span>Processing locally • No data stored</span>
              </div>

              <button
                type="submit"
                disabled={isLoading || input.trim().length === 0}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 via-emerald-500 to-cyan-500 text-black rounded-xl font-semibold hover:shadow-[0_0_30px_rgba(34,197,94,0.5),0_0_60px_rgba(6,182,212,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-105"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 rounded-full border-2 border-black/30 border-t-black animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Submit
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
