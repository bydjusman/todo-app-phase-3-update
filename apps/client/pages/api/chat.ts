import { NextApiRequest, NextApiResponse } from 'next';
import { auth } from '../../../lib/auth';
import { db } from '../../../lib/db';
import { conversations, messages } from '../../../lib/schema';
import { eq, and } from 'drizzle-orm';
import { nanoid } from 'nanoid';
import { runAIAssistant } from '../../../lib/ai';

// Define types for the request/response
interface ChatRequestBody {
  message: string;
  conversationId?: string;
}

interface ChatResponse {
  conversationId: string;
  response: string;
  tool_calls?: any[];
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ChatResponse | { error: string }>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // 1. Get JWT → user_id
    const session = await auth.getSession({
      headers: req.headers,
    });

    if (!session) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const userId = session.user.id;
    const { message, conversationId: providedConversationId }: ChatRequestBody = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // 2. Fetch or create conversation
    let conversationId: string;

    if (providedConversationId) {
      // Try to fetch existing conversation
      const existingConversation = await db.query.conversations.findFirst({
        where: and(
          eq(conversations.id, providedConversationId),
          eq(conversations.userId, userId)
        )
      });

      if (existingConversation) {
        conversationId = existingConversation.id;
      } else {
        // If conversation doesn't exist or doesn't belong to user, create new one
        const newConversation = await db.insert(conversations).values({
          id: nanoid(),
          userId: userId,
          title: message.substring(0, 50) + (message.length > 50 ? '...' : ''), // Use first 50 chars of message as title
          createdAt: new Date(),
          updatedAt: new Date(),
        }).returning();
        conversationId = newConversation[0].id;
      }
    } else {
      // Create new conversation
      const newConversation = await db.insert(conversations).values({
        id: nanoid(),
        userId: userId,
        title: message.substring(0, 50) + (message.length > 50 ? '...' : ''), // Use first 50 chars of message as title
        createdAt: new Date(),
        updatedAt: new Date(),
      }).returning();
      conversationId = newConversation[0].id;
    }

    // 3. Save user message
    await db.insert(messages).values({
      id: nanoid(),
      conversationId,
      userId,
      role: 'user',
      content: message,
      createdAt: new Date(),
    });

    // 4. Run AI agent
    // This would connect to your AI service (OpenAI, Anthropic, etc.)
    const aiResponse = await runAIAssistant(message, conversationId, userId);

    // 5. Save assistant response and tool calls
    await db.insert(messages).values({
      id: nanoid(),
      conversationId,
      userId,
      role: 'assistant',
      content: aiResponse.response,
      toolCalls: aiResponse.tool_calls || null,
      createdAt: new Date(),
    });

    // 6. Return conversation_id, response, tool_calls
    return res.status(200).json({
      conversationId,
      response: aiResponse.response,
      tool_calls: aiResponse.tool_calls,
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

// Mock implementation of AI assistant - replace with your actual AI provider
async function runAIAssistant(userMessage: string, conversationId: string, userId: string): Promise<{
  response: string;
  tool_calls?: any[];
}> {
  // This is a placeholder - in a real implementation, you would:
  // 1. Get conversation history to provide context to the AI
  // 2. Call your AI provider's API (OpenAI, Anthropic, etc.)
  // 3. Potentially execute tool calls if the AI requests them
  // 4. Return the AI's response and any tool calls it made

  // For example, with OpenAI:
  /*
  const { Configuration, OpenAIApi } = require("openai");
  const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
  });
  const openai = new OpenAIApi(configuration);

  const messages = [
    { role: "system", content: "You are a helpful assistant." },
    // Add conversation history here
    { role: "user", content: userMessage }
  ];

  const completion = await openai.createChatCompletion({
    model: "gpt-3.5-turbo",
    messages: messages,
  });

  const aiResponse = completion.data.choices[0].message;
  return {
    response: aiResponse?.content || '',
    tool_calls: aiResponse?.tool_calls || undefined
  };
  */

  // Mock response for demonstration
  return {
    response: `This is a mock response to: "${userMessage}". In a real implementation, this would come from an AI assistant.`,
    tool_calls: [] // Add actual tool calls if any
  };
}