import { delay, http, HttpResponse } from "msw";
import { API_URL } from "@/lib/api-config";
import mockData from "./example-data/demo3.json";

export const handlers = [
  http.post(`${API_URL}/pipeline`, async () => {
    await delay(1000);
    return HttpResponse.json(mockData);
  }),
];
