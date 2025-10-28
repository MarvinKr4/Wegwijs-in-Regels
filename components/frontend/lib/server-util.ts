"use server";

import { LegalData } from "./types";
import { API_URL } from "./api-config";

// This is a server action that returns mock data from temp.json
export async function getResponse(query: string): Promise<LegalData> {
  const URL = `${API_URL}/pipeline`;
  console.log("Fetching data from URL:", URL);

  const body = JSON.stringify({
    session_id: "1",
    message: query,
  });

  const response = await fetch(URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  });

  if (response.ok) {
    const data = await response.json();
    return data as LegalData;
  } else {
    console.error("Error response:", response.statusText);
    throw new Error(
      `Failed to fetch data from the API: [${response.status}] ${response.statusText}`
    );
  }
}
