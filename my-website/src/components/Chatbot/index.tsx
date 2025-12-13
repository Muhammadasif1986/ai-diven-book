/**
 * Chatbot component for the Docusaurus site
 * This component provides a chat interface that communicates with the backend API
 */

import React, { useState, useEffect, useRef } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import SelectionHandler from './SelectionHandler';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');

  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize session ID on component mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem('chat-session-id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chat-session-id', newSessionId);
      setSessionId(newSessionId);
    }

    // Add welcome message
    setMessages([
      {
        id: 'welcome',
        text: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics book. Ask me anything about the content!',
        sender: 'bot',
        timestamp: new Date(),
      }
    ]);
  }, []);

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat is opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call backend API - use environment variable for API base URL
      let API_BASE_URL = 'http://localhost:8000'; // Default fallback

      if (typeof window !== 'undefined') {
        // Client-side: check for environment variable in multiple possible locations
        // First check for a global config that might be set by Docusaurus
        const globalConfig = (window as any).DOCUUSAURUS_CONFIG;
        let envApiUrl = globalConfig?.customFields?.NEXT_PUBLIC_API_BASE_URL;

        // If not found in global config, check for other possible locations
        if (!envApiUrl) {
          envApiUrl = (window as any)._env_?.NEXT_PUBLIC_API_BASE_URL;
        }
        if (!envApiUrl) {
          // Safely check for process without directly accessing it
          try {
            envApiUrl = typeof process !== 'undefined' && process.env ? process.env.NEXT_PUBLIC_API_BASE_URL : undefined;
          } catch {
            envApiUrl = undefined;
          }
        }

        if (envApiUrl) {
          API_BASE_URL = envApiUrl;
        } else {
          // Construct API URL by replacing frontend port with backend port (default 8000)
          const port = window.location.port;
          const protocol = window.location.protocol;
          const hostname = window.location.hostname;
          // If on localhost, use the standard backend port; otherwise, use the same host
          API_BASE_URL = hostname === 'localhost' ? `${protocol}//${hostname}:8000` : `${protocol}//${hostname}/api`;
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.text,
          book_id: 'physical-ai-humanoid-robotics', // Use the book ID
          session_token: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now().toString(),
        text: data.response || 'I couldn\'t process your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSelectionQuery = async (selectedText: string) => {
    if (!selectedText.trim() || isLoading) return;

    const userMessage: Message = {
      id: `selection-${Date.now()}`,
      text: `Regarding: "${selectedText}" - Can you explain this in more detail or provide more information?`,
      sender: 'user',
      timestamp: new Date(),
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);

    try {
      // Call backend API - use environment variable for API base URL
      let API_BASE_URL = 'http://localhost:8000'; // Default fallback

      if (typeof window !== 'undefined') {
        // Client-side: check for environment variable in multiple possible locations
        // First check for a global config that might be set by Docusaurus
        const globalConfig = (window as any).DOCUUSAURUS_CONFIG;
        let envApiUrl = globalConfig?.customFields?.NEXT_PUBLIC_API_BASE_URL;

        // If not found in global config, check for other possible locations
        if (!envApiUrl) {
          envApiUrl = (window as any)._env_?.NEXT_PUBLIC_API_BASE_URL;
        }
        if (!envApiUrl) {
          // Safely check for process without directly accessing it
          try {
            envApiUrl = typeof process !== 'undefined' && process.env ? process.env.NEXT_PUBLIC_API_BASE_URL : undefined;
          } catch {
            envApiUrl = undefined;
          }
        }

        if (envApiUrl) {
          API_BASE_URL = envApiUrl;
        } else {
          // Construct API URL by replacing frontend port with backend port (default 8000)
          const port = window.location.port;
          const protocol = window.location.protocol;
          const hostname = window.location.hostname;
          // If on localhost, use the standard backend port; otherwise, use the same host
          API_BASE_URL = hostname === 'localhost' ? `${protocol}//${hostname}:8000` : `${protocol}//${hostname}/api`;
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/query/selection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: selectedText,
          selected_text: selectedText, // Send the selected text as context
          book_id: 'physical-ai-humanoid-robotics', // Use the book ID
          session_token: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        text: data.response || 'I couldn\'t process your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending selection query:', error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error processing your selection. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="chatbot-container">
      {/* Selection handler for text selection queries */}
      <SelectionHandler onQuerySubmit={handleSelectionQuery} isLoading={isLoading} />

      {/* Floating button to open chat */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="chatbot-button fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-600 text-white shadow-lg flex items-center justify-center hover:bg-blue-700 transition-colors z-50"
          aria-label="Open chatbot"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="chatbot-window fixed bottom-6 right-6 w-80 h-96 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50 overflow-hidden">
          {/* Header */}
          <div className="chatbot-header bg-blue-600 text-white p-3 flex justify-between items-center">
            <h3 className="font-semibold">Physical AI Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 focus:outline-none"
              aria-label="Close chat"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Messages container */}
          <div className="chatbot-messages flex-1 overflow-y-auto p-3 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`mb-3 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start mb-3">
                <div className="bg-gray-200 text-gray-800 rounded-lg px-3 py-2 max-w-[80%]">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="chatbot-input p-3 border-t border-gray-200 bg-white">
            <div className="flex">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about Physical AI & Robotics..."
                className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputValue.trim()}
                className={`bg-blue-600 text-white px-4 py-2 rounded-r-lg ${
                  isLoading || !inputValue.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;