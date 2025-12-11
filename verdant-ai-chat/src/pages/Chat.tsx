import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatSidebar } from '@/components/ChatSidebar';
import { ChatInterface } from '@/components/ChatInterface';
import { useAuth } from '@/lib/store';
import { chatAPI } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ file_name: string; content: string }>;
}

export default function Chat() {
  const { token, checkAuth } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate]);

  const handleNewChat = () => {
    setMessages([]);
  };

  const handleClearHistory = async () => {
    try {
      await chatAPI.clearHistory();
      setMessages([]);
    } catch (err) {
      console.error('Error clearing history:', err);
    }
  };

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background flex">
      <ChatSidebar onNewChat={handleNewChat} />
      <main className="flex-1 md:ml-64 flex flex-col h-screen">
        <ChatInterface messages={messages} setMessages={setMessages} />
      </main>
    </div>
  );
}
