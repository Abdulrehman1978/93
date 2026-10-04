import { CitizenShell } from "@/components/layout/shells";
import { CitizenIntakeFlow } from "@/components/citizen/intake-flow";

export default function SpeakPage() {
  return (
    <CitizenShell>
      <CitizenIntakeFlow mode="speak" />
    </CitizenShell>
  );
}
