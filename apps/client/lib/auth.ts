import { betterAuth } from 'better-auth';
import { toNextJsHandler } from 'better-auth/next-js';

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET || 'super-secret-jwt-key-for-local-development-min-32-chars',
  emailAndPassword: {
    enabled: true,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
  },
  database: {
    provider: 'sqlite',
    url: process.env.DATABASE_URL || 'sqlite://./todo-app.db',
  },
});

export const handler = toNextJsHandler(auth);

// Helper function to get session from headers (for Pages API)
export async function getSession(headers: Headers | Record<string, string | undefined>) {
  let cookie: string | undefined;
  
  if (headers instanceof Headers) {
    cookie = headers.get('cookie') || undefined;
  } else {
    cookie = headers.cookie || headers.Cookie || undefined;
  }
  
  if (!cookie) return null;
  
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000'}/api/auth/get-session`, {
      headers: {
        cookie,
      },
    });
    
    if (!response.ok) return null;
    
    const data = await response.json();
    return data.session || null;
  } catch {
    return null;
  }
}
