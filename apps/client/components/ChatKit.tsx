'use client';

import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
}

const ChatKit: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Load user and messages from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    // Load previous messages from localStorage
    const storedMessages = localStorage.getItem('chat_messages');
    if (storedMessages) {
      try {
        setMessages(JSON.parse(storedMessages));
      } catch (e) {
        console.error('Error parsing stored messages:', e);
        setMessages([]);
      }
    } else {
      setMessages([]);
    }

    // Load session ID if available
    const storedSessionId = localStorage.getItem('chat_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chat_messages', JSON.stringify(messages));
  }, [messages]);

  // Save session ID to localStorage whenever it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('chat_session_id', sessionId);
    }
  }, [sessionId]);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !user?.id || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the chat API
      const token = localStorage.getItem('auth_token');
      const userId = user?.id;

      if (!userId) {
        throw new Error('User not logged in');
      }

      if (!token) {
        throw new Error('Authentication token not found');
      }

      let apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/${userId}/chat?message=${encodeURIComponent(inputValue)}`;

      if (sessionId) {
        apiUrl += `&context=${encodeURIComponent(JSON.stringify({ session_id: sessionId }))}`;
      }

      console.log('Calling API:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.message || 'Failed to process chat message');
      }

      const data = await response.json();

      // Update session ID if not set
      if (!sessionId && data.context?.session_id) {
        setSessionId(data.context.session_id);
      }

      const botMessage: Message = {
        id: data.id,
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp,
        intent: data.intent,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      toast.error(error.message || 'Error processing your message');

      // Add error message to UI
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to clear chat history
  const clearChatHistory = () => {
    setMessages([]);
    localStorage.removeItem('chat_messages');
    localStorage.removeItem('chat_session_id');
    setSessionId(null);
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center p-4">
        <p className="text-gray-500">Please sign in to use the chatbot</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white rounded-lg shadow-md">
      {/* Chat Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 rounded-t-lg flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">AI Chat Assistant</h2>
          <p className="text-sm text-gray-500">Ask me to create, list, update, or delete tasks</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChatHistory}
            className="text-xs text-gray-500 hover:text-red-500 hover:underline"
            title="Clear chat history"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="bg-blue-50 rounded-full p-4 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-1">Welcome to the Task Chatbot!</h3>
            <p className="text-gray-500 max-w-md">
              I can help you manage your tasks using natural language. Try commands like:
            </p>
            <ul className="mt-2 text-sm text-gray-500 space-y-1">
              <li>"Create a task to buy groceries"</li>
              <li>"What tasks do I have today?"</li>
              <li>"Mark the first task as completed"</li>
              <li>"Delete the meeting task"</li>
            </ul>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="bg-gray-800 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
                        AI
                      </div>
                    </div>
                  )}
                  <div className="flex-1">
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.intent && (
                      <span className="text-xs opacity-70 mt-1 block">
                        Intent: {message.intent}
                      </span>
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
                        U
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 rounded-lg px-4 py-2 max-w-[80%]">
              <div className="flex items-center space-x-2">
                <div className="flex-shrink-0">
                  <div className="bg-gray-800 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
                    AI
                  </div>
                </div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Examples: "Add task: buy groceries", "Show my tasks", "Mark task as done"
        </p>
      </div>
    </div>
  );
};

export default ChatKit;