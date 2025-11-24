import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

export async function GET() {
  try {
    // Path to the wellness log file in the backend
    const wellnessLogPath = join(process.cwd(), '..', 'backend', 'wellness_log.json');

    try {
      const fileContent = await readFile(wellnessLogPath, 'utf-8');
      const wellnessData = JSON.parse(fileContent);

      return NextResponse.json({
        success: true,
        entries: wellnessData.entries || [],
      });
    } catch {
      // If file doesn't exist or can't be read, return empty entries
      return NextResponse.json({
        success: true,
        entries: [],
      });
    }
  } catch (error) {
    console.error('Error reading wellness data:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to load wellness data',
        entries: [],
      },
      { status: 500 }
    );
  }
}
