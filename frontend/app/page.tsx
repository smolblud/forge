"use client"

import { useState } from "react"
import ChatInterface from "@/components/chat-interface"
import WelcomeScreen from "@/components/welcome-screen"

export default function Home() {
  const [hasStarted, setHasStarted] = useState(false)

  return (
    <main className="min-h-screen bg-black text-white">
      {!hasStarted ? <WelcomeScreen onStart={() => setHasStarted(true)} /> : <ChatInterface />}
    </main>
  )
}
