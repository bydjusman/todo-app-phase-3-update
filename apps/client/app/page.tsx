'use client';

import { useEffect } from 'react';
import { useSession } from '../lib/auth-client';

export default function HomePage() {
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending) {
      if (session) {
        // User is authenticated, redirect to tasks page
        window.location.href = '/tasks';
      } else {
        // User is not authenticated, redirect to login
        window.location.href = '/login';
      }
    }
  }, [session, isPending]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
        <p className="mt-4 text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}