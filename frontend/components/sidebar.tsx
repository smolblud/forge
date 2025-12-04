"use client"

import { useEffect, useState } from "react"
import { Plus, MessageSquare, Trash2, Leaf } from "lucide-react"
import { getChats, deleteChat, Chat } from "@/lib/api"
import { cn } from "@/lib/utils"

interface SidebarProps {
  currentChatId: number | null
  onSelectChat: (id: number) => void
  onNewChat: () => void
}

export default function Sidebar({ currentChatId, onSelectChat, onNewChat }: SidebarProps) {
  const [chats, setChats] = useState<Chat[]>([])

  useEffect(() => {
    loadChats()
  }, [currentChatId])

  const loadChats = async () => {
    try {
      const data = await getChats()
      setChats(data)
    } catch (error) {
      console.error("Failed to load chats", error)
    }
  }

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation()
    try {
      await deleteChat(id)
      setChats(chats.filter(c => c.id !== id))
      if (currentChatId === id) {
        onNewChat()
      }
    } catch (error) {
      console.error("Failed to delete chat", error)
    }
  }

  return (
    <div className="w-64 border-r border-green-500/20 flex flex-col h-full bg-black/40 backdrop-blur-xl">
      <div className="p-4 border-b border-green-500/10">
        <button 
            onClick={onNewChat} 
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-500/10 to-cyan-500/10 border border-green-500/30 rounded-xl text-green-400 hover:text-white hover:bg-green-500/20 transition-all duration-300 group"
        >
          <Plus className="w-4 h-4 group-hover:rotate-90 transition-transform" />
          <span className="font-medium">New Chat</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={cn(
                "group flex items-center justify-between p-3 rounded-lg cursor-pointer text-sm transition-all duration-200 border border-transparent",
                currentChatId === chat.id 
                  ? "bg-green-500/10 text-white border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.1)]" 
                  : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
              )}
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <MessageSquare className={cn("w-4 h-4 shrink-0", currentChatId === chat.id ? "text-green-400" : "text-zinc-600")} />
                <span className="truncate font-medium">{chat.title}</span>
              </div>
              <button
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 hover:text-red-400 rounded transition-all"
                onClick={(e) => handleDelete(e, chat.id)}
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
      </div>
      
      <div className="p-4 border-t border-green-500/10">
        <div className="flex items-center gap-2 text-xs text-zinc-500">
            <Leaf className="w-3 h-3 text-green-500/50" />
            <span>Forge AI Coach</span>
        </div>
      </div>
    </div>
  )
}
