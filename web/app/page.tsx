import { redirect } from "next/navigation";

// Root → redirect straight to the dashboard
export default function Home() {
  redirect("/dashboard");
}
