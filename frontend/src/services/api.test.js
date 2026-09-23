import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch, createAlertWebSocket } from './api';

global.fetch = vi.fn();

describe('API & WebSocket Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('handles API loading and successful response', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });
    
    const result = await apiFetch('/test');
    expect(result.success).toBe(true);
    expect(fetch).toHaveBeenCalledWith('/test', expect.any(Object));
  });

  it('handles API error states and empty responses', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not Found' })
    });
    
    await expect(apiFetch('/test')).rejects.toThrow('Not Found');
  });

  it('creates WebSocket connection and handles lifecycle', () => {
    // Mock WebSocket
    const WS = vi.fn(() => ({
      onopen: null,
      onclose: null,
      onmessage: null,
      close: vi.fn(),
    }));
    global.WebSocket = WS;

    const onMessage = vi.fn();
    const onOpen = vi.fn();
    const onClose = vi.fn();

    const ws = createAlertWebSocket(onMessage, onOpen, onClose);
    
    // Simulate open
    ws.onopen();
    expect(onOpen).toHaveBeenCalled();

    // Simulate message (lifecycle event)
    ws.onmessage({ data: JSON.stringify({ type: 'LOGIN_EVENT', event_id: '123' }) });
    expect(onMessage).toHaveBeenCalledWith({ type: 'LOGIN_EVENT', event_id: '123' });

    // Simulate close/disconnect
    ws.onclose();
    expect(onClose).toHaveBeenCalled();
  });
});
