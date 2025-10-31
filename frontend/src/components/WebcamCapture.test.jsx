import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import WebcamCapture from './WebcamCapture';

// Mock gesture detection service if used by the component
// Adjust the path if WebcamCapture imports a different module
jest.mock('../services/gestureDetection', () => ({
  detectGesture: jest.fn(async () => ({ gesture: 'rock' })),
}));

// Utilities to mock media and canvas APIs
const createFakeMediaStream = () => ({
  getTracks: () => [
    { stop: jest.fn(), kind: 'video', enabled: true },
  ],
});

const setupVideoAndCanvasMocks = () => {
  // Mock HTMLVideoElement.play and related readiness
  Object.defineProperty(HTMLMediaElement.prototype, 'paused', {
    configurable: true,
    get: () => false,
  });
  HTMLMediaElement.prototype.play = jest.fn().mockResolvedValue();
  HTMLMediaElement.prototype.pause = jest.fn();
  Object.defineProperty(HTMLMediaElement.prototype, 'readyState', {
    configurable: true,
    get: () => 4, // HAVE_ENOUGH_DATA
  });

  // Mock canvas 2D context and toDataURL
  const getContext = jest.fn(() => ({
    drawImage: jest.fn(),
    clearRect: jest.fn(),
  }));
  HTMLCanvasElement.prototype.getContext = getContext;
  HTMLCanvasElement.prototype.toDataURL = jest.fn(() => 'data:image/png;base64,FAKE');
};

beforeAll(() => {
  // Mock getUserMedia globally
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: {
      getUserMedia: jest.fn().mockResolvedValue(createFakeMediaStream()),
    },
    configurable: true,
  });
  setupVideoAndCanvasMocks();
});

afterEach(() => {
  jest.clearAllMocks();
});

// Helper to render component
const renderComponent = async () => {
  await act(async () => {
    render(<WebcamCapture />);
  });
};

describe('WebcamCapture', () => {
  test('renders webcam video when permission is granted', async () => {
    await renderComponent();

    // Expect a video element to be in the document
    const video = await screen.findByTestId('webcam-video', {}, { timeout: 2000 }).catch(() => null);

    // Fallback: look by role if data-testid is not present
    const videoByRole = video ?? screen.getByRole('img', { hidden: true }) ?? screen.queryByRole('video');

    expect(video || videoByRole).toBeTruthy();
  });

  test('handles permission denial and displays an error', async () => {
    const original = navigator.mediaDevices.getUserMedia;
    navigator.mediaDevices.getUserMedia = jest.fn().mockRejectedValue(new Error('Permission denied'));

    await renderComponent();

    // Look for an error message rendered by the component
    const error = await screen.findByText(/permission|denied|error/i);
    expect(error).toBeInTheDocument();

    navigator.mediaDevices.getUserMedia = original;
  });

  test('captures a frame and shows a preview image when capture is clicked', async () => {
    await renderComponent();

    // Find capture button by text or testid
    const captureBtn = screen.getByRole('button', { name: /capture|take|snapshot/i });

    await act(async () => {
      fireEvent.click(captureBtn);
    });

    // Expect a preview image to appear
    const preview = await screen.findByAltText(/preview|captured|snapshot/i);
    expect(preview).toBeInTheDocument();
    expect(preview).toHaveAttribute('src', expect.stringContaining('data:image/png;base64'));
  });

  test('disables capture button if stream not ready', async () => {
    // Force readyState to simulate not ready
    const descriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'readyState');
    Object.defineProperty(HTMLMediaElement.prototype, 'readyState', {
      configurable: true,
      get: () => 0, // HAVE_NOTHING
    });

    await renderComponent();

    const captureBtn = screen.getByRole('button', { name: /capture|take|snapshot/i });
    expect(captureBtn).toBeDisabled();

    // restore
    if (descriptor) Object.defineProperty(HTMLMediaElement.prototype, 'readyState', descriptor);
  });

  test('sends captured image to detection service and displays result', async () => {
    const { detectGesture } = require('../services/gestureDetection');
    detectGesture.mockResolvedValueOnce({ gesture: 'scissors' });

    await renderComponent();

    const captureBtn = screen.getByRole('button', { name: /capture|take|snapshot/i });
    await act(async () => {
      fireEvent.click(captureBtn);
    });

    // Expect detection result text somewhere
    const result = await screen.findByText(/scissors/i);
    expect(result).toBeInTheDocument();
    expect(detectGesture).toHaveBeenCalledWith(expect.stringMatching(/^data:image\/png;base64,/));
  });

  test('handles detection service failure and shows an error', async () => {
    const { detectGesture } = require('../services/gestureDetection');
    detectGesture.mockRejectedValueOnce(new Error('Network error'));

    await renderComponent();

    const captureBtn = screen.getByRole('button', { name: /capture|take|snapshot/i });
    await act(async () => {
      fireEvent.click(captureBtn);
    });

    const err = await screen.findByText(/error|failed|network/i);
    expect(err).toBeInTheDocument();
  });

  test('cleans up media tracks on unmount', async () => {
    await act(async () => {
      const { unmount } = render(<WebcamCapture />);
      await waitFor(() => expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled());
      const stream = await navigator.mediaDevices.getUserMedia.mock.results[0].value;
      const tracks = (await stream).getTracks();
      unmount();
      // Expect stop to have been called on the track
      expect(tracks[0].stop).toHaveBeenCalled();
    });
  });
});
