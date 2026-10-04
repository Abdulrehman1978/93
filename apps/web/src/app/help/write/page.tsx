import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export default function WritePage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="write" />
    </CitizenShell>
  );
}
