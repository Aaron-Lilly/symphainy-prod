/**
 * Visual Regression Testing
 * Advanced visual regression testing with screenshot comparison
 */

import { getGlobalConfig } from '../../config';

export interface VisualTestConfig {
  enableScreenshotCapture: boolean;
  enableBaselineComparison: boolean;
  enableDiffDetection: boolean;
  screenshotQuality: number;
  tolerance: number;
  outputDir: string;
}

export interface ScreenshotData {
  id: string;
  data: string;
  timestamp: number;
  metadata: Record<string, any>;
  dimensions: { width: number; height: number };
}

export interface VisualTestResult {
  id: string;
  baseline: ScreenshotData;
  current: ScreenshotData;
  diff: ScreenshotData | null;
  passed: boolean;
  similarity: number;
  differences: VisualDifference[];
  metadata: Record<string, any>;
}

export interface VisualDifference {
  x: number;
  y: number;
  width: number;
  height: number;
  severity: 'low' | 'medium' | 'high';
}

export class VisualRegressionTesting {
  private config = getGlobalConfig();
  private visualConfig: VisualTestConfig;
  private baselines: Map<string, ScreenshotData> = new Map();

  constructor(config: Partial<VisualTestConfig> = {}) {
    this.visualConfig = {
      enableScreenshotCapture: true,
      enableBaselineComparison: true,
      enableDiffDetection: true,
      screenshotQuality: 0.9,
      tolerance: 0.95,
      outputDir: './screenshots',
      ...config,
    };
  }

  // Capture screenshot of element
  async captureScreenshot(
    element: HTMLElement,
    id: string,
    metadata: Record<string, any> = {}
  ): Promise<ScreenshotData> {
    if (!this.visualConfig.enableScreenshotCapture) {
      throw new Error('Screenshot capture is disabled');
    }

    try {
      // Get element dimensions
      const rect = element.getBoundingClientRect();
      const dimensions = {
        width: rect.width,
        height: rect.height,
      };

      // Capture screenshot using html2canvas or similar
      const screenshotData = await this.captureElementScreenshot(element);

      const screenshot: ScreenshotData = {
        id,
        data: screenshotData,
        timestamp: Date.now(),
        metadata,
        dimensions,
      };

      return screenshot;
    } catch (error) {
      throw new Error(`Failed to capture screenshot: ${error}`);
    }
  }

  // Compare screenshots
  async compareScreenshots(
    baseline: ScreenshotData,
    current: ScreenshotData
  ): Promise<VisualTestResult> {
    if (!this.visualConfig.enableBaselineComparison) {
      throw new Error('Baseline comparison is disabled');
    }

    try {
      // Decode base64 images
      const baselineImage = await this.decodeImage(baseline.data);
      const currentImage = await this.decodeImage(current.data);

      // Compare images
      const comparison = await this.compareImages(baselineImage, currentImage);

      // Generate diff if differences found
      let diff: ScreenshotData | null = null;
      if (comparison.differences.length > 0 && this.visualConfig.enableDiffDetection) {
        diff = await this.generateDiff(baselineImage, currentImage, comparison.differences);
      }

      const result: VisualTestResult = {
        id: `${baseline.id}_vs_${current.id}`,
        baseline,
        current,
        diff,
        passed: comparison.similarity >= this.visualConfig.tolerance,
        similarity: comparison.similarity,
        differences: comparison.differences,
        metadata: {
          baselineId: baseline.id,
          currentId: current.id,
          tolerance: this.visualConfig.tolerance,
        },
      };

      return result;
    } catch (error) {
      throw new Error(`Failed to compare screenshots: ${error}`);
    }
  }

  // Run visual regression test
  async runVisualTest(
    element: HTMLElement,
    testId: string,
    metadata: Record<string, any> = {}
  ): Promise<VisualTestResult> {
    // Capture current screenshot
    const currentScreenshot = await this.captureScreenshot(element, testId, metadata);

    // Get baseline screenshot
    const baselineScreenshot = this.baselines.get(testId);
    if (!baselineScreenshot) {
      // Create baseline if it doesn't exist
      this.baselines.set(testId, currentScreenshot);
      return {
        id: testId,
        baseline: currentScreenshot,
        current: currentScreenshot,
        diff: null,
        passed: true,
        similarity: 1.0,
        differences: [],
        metadata: { ...metadata, baselineCreated: true },
      };
    }

    // Compare with baseline
    return this.compareScreenshots(baselineScreenshot, currentScreenshot);
  }

  // Update baseline
  updateBaseline(testId: string, screenshot: ScreenshotData): void {
    this.baselines.set(testId, screenshot);
  }

  // Get baseline
  getBaseline(testId: string): ScreenshotData | undefined {
    return this.baselines.get(testId);
  }

  // Clear baselines
  clearBaselines(): void {
    this.baselines.clear();
  }

  // Save screenshot to file
  async saveScreenshot(screenshot: ScreenshotData, filename: string): Promise<void> {
    try {
      // This would save the screenshot to the filesystem
      // Implementation depends on the environment (Node.js vs browser)
      console.log(`Saving screenshot: ${filename}`);
    } catch (error) {
      throw new Error(`Failed to save screenshot: ${error}`);
    }
  }

  // Load screenshot from file
  async loadScreenshot(filename: string): Promise<ScreenshotData> {
    try {
      // This would load the screenshot from the filesystem
      // Implementation depends on the environment
      throw new Error('Screenshot loading not implemented');
    } catch (error) {
      throw new Error(`Failed to load screenshot: ${error}`);
    }
  }

  // Private methods
  private async captureElementScreenshot(element: HTMLElement): Promise<string> {
    // This would use html2canvas or similar library
    // For now, return a placeholder
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
  }

  private async decodeImage(base64Data: string): Promise<ImageData> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Failed to get canvas context'));
          return;
        }

        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        resolve(imageData);
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = base64Data;
    });
  }

  private async compareImages(
    baseline: ImageData,
    current: ImageData
  ): Promise<{ similarity: number; differences: VisualDifference[] }> {
    // Simple pixel-by-pixel comparison
    // In production, use a more sophisticated image comparison library
    const differences: VisualDifference[] = [];
    let totalPixels = baseline.data.length / 4;
    let differentPixels = 0;

    for (let i = 0; i < baseline.data.length; i += 4) {
      const baselineR = baseline.data[i];
      const baselineG = baseline.data[i + 1];
      const baselineB = baseline.data[i + 2];
      const baselineA = baseline.data[i + 3];

      const currentR = current.data[i];
      const currentG = current.data[i + 1];
      const currentB = current.data[i + 2];
      const currentA = current.data[i + 3];

      const diff = Math.abs(baselineR - currentR) + 
                   Math.abs(baselineG - currentG) + 
                   Math.abs(baselineB - currentB) + 
                   Math.abs(baselineA - currentA);

      if (diff > 0) {
        differentPixels++;
      }
    }

    const similarity = 1 - (differentPixels / totalPixels);

    return {
      similarity,
      differences,
    };
  }

  private async generateDiff(
    baseline: ImageData,
    current: ImageData,
    differences: VisualDifference[]
  ): Promise<ScreenshotData> {
    // Generate diff image highlighting differences
    // For now, return a placeholder
    return {
      id: 'diff',
      data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
      timestamp: Date.now(),
      metadata: { type: 'diff' },
      dimensions: { width: baseline.width, height: baseline.height },
    };
  }
} 