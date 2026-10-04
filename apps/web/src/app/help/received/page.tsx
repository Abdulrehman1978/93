import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export default function ReceivedPage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="received" />
    </CitizenShell>
  );
}
