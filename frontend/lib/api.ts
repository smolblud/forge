const API_BASE_URL = "http://127.0.0.1:8000"

export interface Chat {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  role: string
  content: string
}

export async function getChats(): Promise<Chat[]> {
  const response = await fetch(`${API_BASE_URL}/chats`)
  if (!response.ok) {
    throw new Error("Failed to fetch chats")
  }
  return response.json()
}

export async function getChat(id: number): Promise<Chat & { messages: Message[] }> {
  const response = await fetch(`${API_BASE_URL}/chats/${id}`)
  if (!response.ok) {
    throw new Error("Failed to fetch chat")
  }
  return response.json()
}

export async function createChat(title: string = "New Conversation"): Promise<Chat> {
  const response = await fetch(`${API_BASE_URL}/chats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  })
  if (!response.ok) {
    throw new Error("Failed to create chat")
  }
  return response.json()
}

export async function deleteChat(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chats/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) {
    throw new Error("Failed to delete chat")
  }
}

export async function submitMessage(text: string, conversationId?: number) {
  const response = await fetch(`${API_BASE_URL}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, conversation_id: conversationId }),
  })
  if (!response.ok) {
    throw new Error("Failed to submit message")
  }
  return response.json()
}
