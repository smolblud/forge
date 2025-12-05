"use client"

import { useState } from "react"
// Import the chat interface component
import ChatInterface from "@/components/chat-interface"
import Sidebar from "@/components/sidebar"
import WelcomeScreen from "@/components/welcome-screen"

export default function Home() {
  const [hasStarted, setHasStarted] = useState(false)
  const [currentChatId, setCurrentChatId] = useState<number | null>(null)

  const handleStart = () => {
    setHasStarted(true)
  }

  const handleSelectChat = (id: number) => {
    setCurrentChatId(id)
    setHasStarted(true)
  }

  const handleNewChat = () => {
    setCurrentChatId(null)
    setHasStarted(true)
  }

  const handleConversationCreated = (id: number) => {
    setCurrentChatId(id)
  }

  return (
    <main className="flex h-screen bg-black text-white overflow-hidden">
      {hasStarted && (
        <Sidebar 
          currentChatId={currentChatId} 
          onSelectChat={handleSelectChat} 
          onNewChat={handleNewChat} 
        />
      )}
      <div className="flex-1 flex flex-col h-full relative">
        {!hasStarted ? (
          <WelcomeScreen onStart={handleStart} />
        ) : (
          <ChatInterface 
            conversationId={currentChatId} 
            onConversationCreated={handleConversationCreated}
          />
        )}
      </div>
    </main>
  )
}
