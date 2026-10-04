import type { Metadata } from "next";
import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export const metadata: Metadata = {
  title: "Citizen Information Services",
};

export default function SilentPage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="silent" />
    </CitizenShell>
  );
}
