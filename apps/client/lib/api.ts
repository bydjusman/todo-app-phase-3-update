/**
 * Type-safe API client for Todo Application
 * Handles authentication, error handling, and consistent response patterns
 */

// Environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
  };
}


// Configuration
const REQUEST_TIMEOUT = 10000; // 10 seconds
const MAX_RETRIES = 2;

// Helper function to get auth token from localStorage
function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
}

// Generic fetch with auth, timeout, and retry
async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {},
  retryCount = 0
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;

  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Create AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle 401 - redirect to login
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new Error('Unauthorized');
    }

    // Retry on network errors or 5xx
    if (!response.ok && response.status >= 500 && retryCount < MAX_RETRIES) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
      return fetchWithAuth(endpoint, options, retryCount + 1);
    }

    return response;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }

    // Retry on network errors
    if (retryCount < MAX_RETRIES) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
      return fetchWithAuth(endpoint, options, retryCount + 1);
    }

    throw error;
  }
}

// Response handler
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(errorData.message || `HTTP ${response.status}`);
  }

  const data = await response.json();
  return data;
}

// API client object
export const api = {
  // Task operations
  async getTasks(params?: {
    status?: 'all' | 'pending' | 'completed';
    sort?: string;
    page?: number;
    limit?: number
  }): Promise<Task[]> {
    const query = params ? new URLSearchParams(params as any).toString() : '';
    const response = await fetchWithAuth(`/api/tasks/${query ? `?${query}` : ''}`);
    return handleResponse<Task[]>(response);
  },

  async getTask(id: number): Promise<Task> {
    const response = await fetchWithAuth(`/api/tasks/${id}`);
    return handleResponse<Task>(response);
  },

  async createTask(data: CreateTaskRequest): Promise<Task> {
    const response = await fetchWithAuth('/api/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<Task>(response);
  },

  async updateTask(id: number, data: UpdateTaskRequest): Promise<Task> {
    const response = await fetchWithAuth(`/api/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return handleResponse<Task>(response);
  },

  async deleteTask(id: number): Promise<void> {
    const response = await fetchWithAuth(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
    if (response.status !== 204) {
      await handleResponse(response);
    }
  },

  async toggleTask(id: number, completed: boolean): Promise<Task> {
    const response = await fetchWithAuth(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
    return handleResponse<Task>(response);
  },

  // Auth operations would be handled by Better Auth client functions directly
  // Instead, provide a method to verify user is authenticated
  async verifyAuth(): Promise<boolean> {
    try {
      const response = await fetchWithAuth('/api/auth/me');
      return response.ok;
    } catch (error) {
      return false;
    }
  },

  async getCurrentUser(): Promise<{ id: string; email: string; name?: string }> {
    const response = await fetchWithAuth('/api/auth/me');
    return handleResponse<{ id: string; email: string; name?: string }>(response);
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetchWithAuth('/api/health');
    return handleResponse<{ status: string }>(response);
  },
};

// Hook-like functions for loading states (can be used with React state)
export function useApiCall<T>(
  apiCall: () => Promise<T>
): {
  data: T | null;
  error: string | null;
  loading: boolean;
  execute: () => Promise<void>;
} {
  // This would typically be a React hook, but here's the logic
  let data: T | null = null;
  let error: string | null = null;
  let loading = false;

  const execute = async () => {
    loading = true;
    error = null;
    try {
      data = await apiCall();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
    } finally {
      loading = false;
    }
  };

  return { data, error, loading, execute };
}

// Example usage:
/*
import { api, useApiCall } from '@/lib/api';

function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const { data, error, loading, execute } = useApiCall(() => api.getTasks());

  useEffect(() => {
    execute();
  }, []);

  useEffect(() => {
    if (data) setTasks(data);
  }, [data]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>
          <h3>{task.title}</h3>
          <p>{task.description}</p>
          <button onClick={() => api.toggleTask(task.id, !task.completed)}>
            {task.completed ? 'Mark Incomplete' : 'Mark Complete'}
          </button>
        </div>
      ))}
    </div>
  );
}
*/