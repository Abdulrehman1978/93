import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export default function SilentPage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="silent" />
    </CitizenShell>
  );
}
