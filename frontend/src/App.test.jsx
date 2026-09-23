import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect, vi } from 'vitest';

// Mock matchMedia for recharts/responsive rendering
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), 
    removeListener: vi.fn(), 
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

describe('Dashboard Application', () => {
  it('renders the Topbar and Dashboard layout', () => {
    render(<App />);
    expect(screen.getByText(/SOC Workspace/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Threat & Risk Activity/i)).toBeInTheDocument();
    expect(screen.getByText(/Event Velocity/i)).toBeInTheDocument();
  });
});
