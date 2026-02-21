import { NextApiRequest, NextApiResponse } from 'next';
import { getSession } from '../../lib/auth';
import { db } from '../../lib/db';
import { conversations, messages } from '../../lib/schema';
import { eq, and } from 'drizzle-orm';
import { nanoid } from 'nanoid';
import { runAIAssistant } from '../../lib/ai';

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
    const session = await getSession(req.headers as Record<string, string | undefined>);

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