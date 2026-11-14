/**
 * Layout da área da filial (Issue #91).
 */

import MolduraFilial from "@/components/layout/MolduraFilial";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <MolduraFilial>{children}</MolduraFilial>;
}
