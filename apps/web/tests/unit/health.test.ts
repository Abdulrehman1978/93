import { describe, it, expect } from "vitest";
import { GET } from "../../src/app/api/health/route";
import { HealthStatusSchema } from "@sambal/contracts";

describe("Web Health Route Unit Test", () => {
  it("returns valid HealthStatus matching contract schema", async () => {
    const response = await GET();
    expect(response.status).toBe(200);

    const data = await response.json();
    const parsed = HealthStatusSchema.safeParse(data);

    expect(parsed.success).toBe(true);
    if (parsed.success) {
      expect(parsed.data.status).toBe("ok");
      expect(parsed.data.service).toContain("SAMBAL");
      expect(parsed.data.dependencies.frontend_runtime.status).toBe("healthy");
    }
  });
});
