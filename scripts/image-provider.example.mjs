/**
 * Image provider adapter example.
 *
 * Implement `generateImage` with a provider approved by the project owner.
 * Keep API keys in environment variables and never write them to output or logs.
 * Confirm the provider's usage rights, retention, safety settings, and disclosure
 * requirements before generating images.
 */
export async function generateImage({ prompt, width, height, outputPath }) {
  void prompt;
  void width;
  void height;
  void outputPath;
  throw new Error("No image provider is configured. Use prompts-only mode.");
}

