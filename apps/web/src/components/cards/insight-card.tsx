import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface InsightCardProps {
  label: string;
  value: string | number | undefined | null;
  subtext?: string;
  isLoading?: boolean;
}

export function InsightCard({ label, value, subtext, isLoading }: InsightCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-7 w-28" />
        ) : (
          <p className="text-xl font-semibold text-zinc-100">{value ?? "—"}</p>
        )}
        {subtext && <p className="mt-1 text-xs text-zinc-500">{subtext}</p>}
      </CardContent>
    </Card>
  );
}
