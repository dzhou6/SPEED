const BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

type HttpMethod = "GET" | "POST";

function withTimeout(ms: number) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  return { controller, clear: () => clearTimeout(id) };
}

// Check if string is a valid MongoDB ObjectId format (24 hex characters)
function isValidObjectId(id: string | null): boolean {
  if (!id) return false;
  // Handle JSON-encoded strings (remove quotes if present)
  let cleaned = id.trim();
  // Remove surrounding quotes if JSON-encoded
  if ((cleaned.startsWith('"') && cleaned.endsWith('"')) || 
      (cleaned.startsWith("'") && cleaned.endsWith("'"))) {
    cleaned = cleaned.slice(1, -1);
  }
  // MongoDB ObjectId is exactly 24 hex characters
  const isValid = /^[0-9a-fA-F]{24}$/.test(cleaned);
  if (!isValid) {
    console.log(`ObjectId validation failed: "${id}" (cleaned: "${cleaned}", length: ${cleaned.length})`);
  }
  return isValid;
}

export async function api<TResponse>(
  path: string,
  method: HttpMethod = "GET",
  body?: unknown,
  userIdOverride?: string | null
): Promise<TResponse> {
  // Get userId - use override if provided, otherwise from localStorage
  let userId = userIdOverride !== undefined ? userIdOverride : localStorage.getItem("cc_userId");
  
  // Clean userId if it's JSON-encoded (remove quotes)
  if (userId) {
    userId = userId.trim();
    // Remove surrounding quotes if JSON-encoded
    if ((userId.startsWith('"') && userId.endsWith('"')) || 
        (userId.startsWith("'") && userId.endsWith("'"))) {
      userId = userId.slice(1, -1);
    }
  }
  
  // Check if this endpoint requires authentication (all except /auth/demo and /health)
  const requiresAuth = !path.includes("/auth/demo") && !path.includes("/health");
  
  // If endpoint requires auth but userId is invalid, throw error immediately
  if (requiresAuth) {
    if (!userId) {
      throw new Error("No session found. Please join the course again.");
    }
    if (!isValidObjectId(userId)) {
      console.warn("Invalid userId format detected:", JSON.stringify(userId), "Length:", userId?.length);
      // Don't clear here - let the error handler in the component do it
      throw new Error("Invalid session. Please join the course again.");
    }
  }
  
  const url = `${BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const { controller, clear } = withTimeout(12000);

  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    // Backend requires X-User-Id header for authenticated endpoints
    if (userId && isValidObjectId(userId)) {
      headers["X-User-Id"] = userId;
    }
    
    const res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    const text = await res.text();
    const maybeJson = text ? safeJson(text) : null;

    if (!res.ok) {
      const msg =
        (maybeJson && (maybeJson.error || maybeJson.message || maybeJson.detail)) ||
        text ||
        `Request failed (${res.status})`;
      
      // If 400/401 with "Invalid X-User-Id" or "Missing X-User-Id", it's a session issue
      if ((res.status === 400 || res.status === 401) && 
          (msg.includes("Invalid X-User-Id") || msg.includes("Missing X-User-Id"))) {
        throw new Error("Invalid session. Please join the course again.");
      }
      
      throw new Error(msg);
    }

    return (maybeJson ?? ({} as TResponse)) as TResponse;
  } finally {
    clear();
  }
}

function safeJson(text: string) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export function qs(params: Record<string, string | undefined | null>) {
  const s = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && `${v}`.length) s.set(k, `${v}`);
  });
  const out = s.toString();
  return out ? `?${out}` : "";
}
