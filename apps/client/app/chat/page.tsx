'use client';

import ChatKit from '../../components/ChatKit';
import Header from '../../components/Header';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name?: string;
}

export default function ChatPage() {
  const [hasSession, setHasSession] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for auth token in localStorage
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
      // No session, redirect to login
      router.push('/login');
    } else {
      setHasSession(true);
    }
    setIsLoading(false);
  }, [router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!hasSession) {
    return null; // Redirect handled by useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto py-8 px-4 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Task Assistant</h1>
          <p className="text-gray-600">Manage your tasks using natural language commands</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <ChatKit />
        </div>

        <div className="mt-8 bg-blue-50 rounded-lg p-6 border border-blue-100">
          <h3 className="font-semibold text-blue-800 mb-2">How to use the AI Assistant</h3>
          <ul className="list-disc pl-5 space-y-1 text-blue-700">
            <li>Create tasks: &quot;Add a task to call John tomorrow&quot;</li>
            <li>List tasks: &quot;What tasks do I have?&quot; or &quot;Show my pending tasks&quot;</li>
            <li>Complete tasks: &quot;Mark the first task as completed&quot;</li>
            <li>Delete tasks: &quot;Remove the meeting task&quot;</li>
            <li>Update tasks: &quot;Update the grocery task to next week&quot;</li>
          </ul>
        </div>
      </main>
    </div>
  );
}