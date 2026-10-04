import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export default function HelpPage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="help" />
    </CitizenShell>
  );
}
