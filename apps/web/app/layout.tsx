import type { ReactNode } from "react";
export const metadata = { title: "CareerPilot AI", description: "Your AI career copilot" };
export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body style={{margin:0,fontFamily:"Inter,Arial,sans-serif",background:"#f5f7fb",color:"#172033"}}>{children}</body></html>;
}
