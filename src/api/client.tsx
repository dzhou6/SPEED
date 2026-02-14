const BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

type HttpMethod = "GET" | "POST";

function withTimeout(ms: number) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  return { controller, clear: () => clearTimeout(id) };
}

export async function api<TResponse>(
  path: string,
  method: HttpMethod = "GET",
  body?: unknown
): Promise<TResponse> {
  const url = `${BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const { controller, clear } = withTimeout(12000);

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    const text = await res.text();
    const maybeJson = text ? safeJson(text) : null;

    if (!res.ok) {
      const msg =
        (maybeJson && (maybeJson.error || maybeJson.message)) ||
        text ||
        `Request failed (${res.status})`;
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
