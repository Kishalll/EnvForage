"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { ThemeToggle } from "../providers";

export default function Navbar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === "/") {
      return pathname === "/";
    }
    return pathname === path || pathname.startsWith(path + "/");
  };

  const navLinks = [
    { name: "Profiles", path: "/profiles" },
    { name: "Diagnose", path: "/diagnose" },
    { name: "AI Troubleshoot", path: "/troubleshoot" },
    { name: "Dependencies", path: "/dependencies" },
  ];

  return (
    <header 
      className="glass-nav" 
      style={{ 
        position: "fixed", 
        top: 0,
        left: 0,
        right: 0,
        width: "100%",
        zIndex: 100, 
        padding: "0.85rem 0",
        boxShadow: "0 4px 30px rgba(0, 0, 0, 0.03)",
      }}
    >
      <div className="container nav-container">
        <div className="nav-brand">
          <div style={{ display: "flex", alignItems: "baseline", gap: "1rem" }}>
            <Link href="/" onClick={() => setIsMobileMenuOpen(false)} style={{ fontSize: "1.5rem", fontWeight: 800, fontFamily: "var(--font-display)", letterSpacing: "-0.03em" }}>
              Env<span className="text-gradient">Forage</span>
            </Link>
            <span style={{ color: "var(--text-muted)", fontSize: "0.85rem", fontWeight: 500 }} className="hide-on-mobile">
              MLOps • v2.1.0
            </span>
          </div>
          <nav className="nav-links-desktop">
            {navLinks.map((link) => {
              const active = isActive(link.path);
              return (
                <Link 
                  key={link.path}
                  href={link.path} 
                  style={{ 
                    color: active ? "var(--brand-primary)" : "var(--text-secondary)",
                    position: "relative",
                    padding: "0.25rem 0",
                  }}
                  className="nav-link"
                >
                  {link.name}
                  {active && (
                    <span 
                      style={{
                        position: "absolute",
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: "2px",
                        background: "linear-gradient(90deg, var(--brand-primary), var(--brand-secondary))",
                        borderRadius: "2px",
                      }} 
                    />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="nav-actions hide-on-mobile">
          <ThemeToggle />
          <a 
            href="#" 
            target="_blank" 
            rel="noreferrer" 
            style={{ 
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "0.925rem",
              fontWeight: 600,
              color: "var(--text-secondary)",
              textDecoration: "none",
            }}
          >
            <span style={{ color: "#5865F2" }}>💬</span> Discord
          </a>
          <a 
            href="https://github.com/rishabh0510rishabh/EnvForage" 
            target="_blank" 
            rel="noreferrer" 
            style={{ 
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "0.925rem",
              fontWeight: 600,
              color: "var(--text-secondary)",
              textDecoration: "none",
            }}
          >
            <span style={{ color: "var(--brand-secondary)" }}>★</span> 3.8k stars
          </a>
        </div>
        
        {/* Mobile Nav Toggle */}
        <div className="mobile-menu-btn" style={{ display: "none" /* overridden by media query */ }}>
          <ThemeToggle />
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            style={{ background: 'none', border: 'none', color: 'inherit', marginLeft: '1rem', cursor: 'pointer' }}
          >
            {isMobileMenuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div className="mobile-menu-overlay hide-on-desktop" style={{ position: "absolute", top: "100%", width: "100%" }}>
          {navLinks.map((link) => {
            const active = isActive(link.path);
            return (
              <Link 
                key={link.path}
                href={link.path} 
                onClick={() => setIsMobileMenuOpen(false)}
                style={{ 
                  color: active ? "var(--brand-primary)" : "var(--text-secondary)",
                  fontSize: "1.1rem",
                  fontWeight: 500,
                  padding: "0.75rem 0",
                  borderBottom: "1px solid var(--border-subtle)"
                }}
              >
                {link.name}
              </Link>
            );
          })}
          <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
             <a href="#" className="btn btn-secondary" style={{ flex: 1, textAlign: "center", display: "flex", justifyContent: "center", gap: "0.5rem" }}>
                <span style={{ color: "#5865F2" }}>💬</span> Discord
             </a>
             <a href="https://github.com/rishabh0510rishabh/EnvForage" className="btn btn-secondary" style={{ flex: 1, textAlign: "center", display: "flex", justifyContent: "center", gap: "0.5rem" }}>
                <span style={{ color: "var(--brand-secondary)" }}>★</span> GitHub
             </a>
          </div>
        </div>
      )}
    </header>
  );
}
