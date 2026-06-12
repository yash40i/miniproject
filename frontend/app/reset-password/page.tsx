import ResetPasswordForm from "./ResetPasswordForm";
import { Suspense } from "react";

export const metadata = {
  title: "Reset Password - Resume-Insight AI",
  description: "Reset your password with the link from your email",
};

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
