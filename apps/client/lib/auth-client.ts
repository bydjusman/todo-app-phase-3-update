import { createAuthClient } from "better-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const { signIn, signUp, signOut, useSession } = createAuthClient({
  baseURL: `${API_BASE_URL}/api/auth`,
  fetchOptions: {
    // Add any custom fetch options here
  },
});