import type { ReactNode } from "react";
import ToastHost from "./Toast";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo">💘</div>
          <div>
            <div className="title">CourseCupid / StackMatch</div>
            <div className="subtitle">Hackathon pod matchmaking MVP</div>
          </div>
        </div>
      </header>

      <main className="container">{children}</main>
      <ToastHost />
    </div>
  );
}
