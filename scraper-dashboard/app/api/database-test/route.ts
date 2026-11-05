import { NextResponse } from "next/server";
import pool from "@/lib/db";

export async function GET() {
  try {
    const [rows] = await pool.query("SELECT 1 AS connected");

    return NextResponse.json({
      success: true,
      message: "Next.js connected to MySQL successfully.",
      result: rows,
    });
  } catch (error) {
    console.error("Database connection error:", error);

    return NextResponse.json(
      {
        success: false,
        message: "Failed to connect to MySQL.",
      },
      { status: 500 }
    );
  }
}