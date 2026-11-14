/**
 * Layout da área do associado (Issue #91).
 */

import MolduraAssociado from "@/components/layout/MolduraAssociado";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <MolduraAssociado>{children}</MolduraAssociado>;
}
