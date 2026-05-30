"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Zap, Shield, Brain, Cpu } from "lucide-react";

export default function HomePage() {
  const features = [
    {
      icon: Zap,
      title: "Lightning Fast Setup",
      description: "Generate ML environment scripts in seconds, not hours",
    },
    {
      icon: Shield,
      title: "Safety First",
      description: "AI-powered validation prevents harmful configurations",
    },
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Get intelligent recommendations for your setup",
    },
    {
      icon: Cpu,
      title: "Hardware Aware",
      description: "Optimized scripts for your specific hardware",
    },
  ];

  return (
    <div
      className="relative overflow-hidden"
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background:
          "radial-gradient(circle at top left, rgba(34,197,94,0.15), transparent 30%), radial-gradient(circle at bottom right, rgba(59,130,246,0.15), transparent 30%), var(--bg-primary)",
      }}
    >
      <div
        style={{
          position: "absolute",
          width: "300px",
          height: "300px",
          borderRadius: "999px",
          background: "rgba(34,197,94,0.25)",
          filter: "blur(120px)",
          top: "-100px",
          left: "-100px",
          animation: "float 6s ease-in-out infinite",
        }}
      />
      {/* Hero Section */}
      <section
        style={{
          paddingTop: "8rem",
          paddingBottom: "6rem",
          position: "relative",
        }}
      >
        <div
          className="container"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "4rem",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "2rem",
            fontWeight: 700,
            color: "var(--brand-primary)",
          }}
        >
          {/* LEFT */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1
              style={{
                fontSize: "5rem",
                fontWeight: 800,
                lineHeight: "1.1",
                marginBottom: "1.5rem",
                background: "linear-gradient(to right, #22c55e, #06b6d4, #3b82f6)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                textShadow: "0 0 30px rgba(34,197,94,0.35)",
              }}
            >
              Build ML Environments Faster ⚡
            </h1>

            <p
              style={{
                fontSize: "1.2rem",
                color: "var(--text-secondary)",
                marginBottom: "2rem",
              }}
            >
              Generate safe and optimized AI/ML setup scripts with a modern developer experience.
            </p>

            <div style={{ display: "flex", gap: "1rem" }}>
              <Link
                href="/diagnose"
                style={{
                  padding: "1rem 2rem",
                  borderRadius: "16px",
                  background: "linear-gradient(to right,#22c55e,#16a34a)",
                  color: "white",
                  fontWeight: 600,
                  textDecoration: "none",
                  boxShadow: "0 10px 30px rgba(34,197,94,0.3)",
                }}
              >
                Get Started
              </Link>

              <Link
                href="/profiles"
                style={{
                  padding: "1rem 2rem",
                  borderRadius: "16px",
                  border: "1px solid rgba(255,255,255,0.1)",
                  color: "var(--text-primary)",
                  textDecoration: "none",
                  backdropFilter: "blur(10px)",
                  background: "var(--bg-tertiary)",
                }}
              >
                Browse Profiles
              </Link>
            </div>
          </motion.div>

          {/* RIGHT */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            style={{
              position: "relative",
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "24px",
                padding: "2rem",
                backdropFilter: "blur(12px)",
                boxShadow: "0 10px 40px rgba(0,0,0,0.4)",
              }}
            >
              <div
                style={{
                  height: "300px",
                  borderRadius: "20px",
                  background:
                    "linear-gradient(135deg, rgba(34,197,94,0.2), rgba(59,130,246,0.2))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "2rem",
                  fontWeight: 700,
                }}
              >
                ⚡ AI Powered Setup
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ paddingTop: '4rem', paddingBottom: '4rem', background: 'rgba(0,0,0,0.2)' }}>
        <div className="container">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2, duration: 0.6 }}>
            <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '4rem' }}>Why Choose EnvForge?</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
              {features.map((feature, i) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.1 }}
                    className="glass-panel"
                    style={{
                      padding: "2rem",
                      textAlign: "center",
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: "24px",
                      backdropFilter: "blur(10px)",
                      transition: "all 0.3s ease",
                      boxShadow: "0 8px 30px rgba(0,0,0,0.2)",
                    }}
                  >
                    <Icon
                      size={45}
                      color="#22c55e"
                      style={{
                        margin: "0 auto 1rem",
                        filter: "drop-shadow(0 0 12px rgba(34,197,94,0.6))",
                      }}
                    />
                    <h3 style={{ marginBottom: '0.75rem' }}>{feature.title}</h3>
                    <p style={{ color: 'var(--text-secondary)' }}>{feature.description}</p>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
        <div className="container">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4, duration: 0.6 }}>
            <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '4rem' }}>How It Works</h2>
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              {[
                { num: 1, title: "Run Diagnostics", desc: "Use `envforge diagnose` to analyze your system" },
                { num: 2, title: "Choose Profile", desc: "Select your ML framework (PyTorch, TensorFlow, etc.)" },
                { num: 3, title: "Verify Compatibility", desc: "EnvForge checks your hardware compatibility" },
                { num: 4, title: "Generate Script", desc: "Get a safe, optimized setup script" },
              ].map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.1 }}
                  style={{ display: 'flex', gap: '2rem', marginBottom: i < 3 ? '2rem' : 0, alignItems: 'flex-start' }}
                >
                  <div style={{ background: 'var(--brand-primary)', color: 'white', width: '48px', height: '48px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, flexShrink: 0 }}>
                    {step.num}
                  </div>
                  <div style={{ paddingTop: '0.5rem' }}>
                    <h4 style={{ marginBottom: '0.5rem' }}>{step.title}</h4>
                    <p style={{ color: 'var(--text-secondary)' }}>{step.desc}</p>
                  </div>
                  {i < 3 && <div style={{ width: '2px', background: 'var(--border-strong)', margin: '-2rem 0 0 0', flexGrow: 1 }} />}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{ paddingTop: '4rem', paddingBottom: '6rem', background: 'rgba(99, 102, 241, 0.05)', marginTop: '2rem' }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.6, duration: 0.6 }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1.5rem' }}>Ready to Set Up Your Environment?</h2>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              Start with diagnostics or explore our ML profiles
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link href="/diagnose" className="btn btn-primary" style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
                Run Diagnostics
              </Link>
              <Link href="/profiles" className="btn btn-secondary" style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
                View Profiles
              </Link>
              <Link href="/troubleshoot" className="btn btn-secondary" style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
                AI Troubleshoot
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
      {/* Feature Showcase */}
<section
  style={{
    paddingTop: "6rem",
    paddingBottom: "6rem",
    background: "rgba(255,255,255,0.02)",
  }}
>
  <div className="container">
    <h2
      style={{
        textAlign: "center",
        fontSize: "2.8rem",
        marginBottom: "1rem",
      }}
    >
      Built For Modern AI Development
    </h2>

    <p
      style={{
        textAlign: "center",
        color: "var(--text-secondary)",
        maxWidth: "800px",
        margin: "0 auto 4rem",
        lineHeight: "1.8",
      }}
    >
      From intelligent diagnostics to automated troubleshooting and
      environment generation, EnvForge provides everything needed to
      build, validate, and deploy AI/ML environments with confidence.
    </p>

    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))",
        gap: "2rem",
      }}
    >
      {[
        {
          title: "⚡ AI Environment Generation",
          desc: "Generate optimized ML environments instantly with AI-powered recommendations.",
        },
        {
          title: "🛡️ Safe Dependency Installation",
          desc: "Prevent conflicts and broken setups through automated compatibility checks.",
        },
        {
          title: "🤖 Automated Troubleshooting",
          desc: "Identify and resolve environment issues before they affect productivity.",
        },
        {
          title: "📦 Preconfigured ML Stacks",
          desc: "Ready-to-use setups for PyTorch, TensorFlow, CUDA and modern AI workflows.",
        },
        {
          title: "🧠 Smart Diagnostics",
          desc: "Analyze hardware, software and system readiness with actionable insights.",
        },
      ].map((item, i) => (
        <motion.div
          key={i}
          whileHover={{
            scale: 1.04,
            y: -8,
          }}
          style={{
            padding: "2rem",
            borderRadius: "24px",
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.08)",
            backdropFilter: "blur(10px)",
            boxShadow: "0 0 30px rgba(34,197,94,.12)",
            transition: "all .3s ease",
          }}
        >
          <h3
            style={{
              marginBottom: "0.8rem",
              fontSize: "1.15rem",
            }}
          >
            {item.title}
          </h3>

          <p
            style={{
              color: "var(--text-secondary)",
              lineHeight: "1.7",
            }}
          >
            {item.desc}
          </p>
        </motion.div>
      ))}
    </div>

    <div
      style={{
        marginTop: "5rem",
      }}
    >
      <h3
        style={{
          textAlign: "center",
          marginBottom: "1.5rem",
          fontSize: "1.5rem",
        }}
      >
        Live Environment Analysis
      </h3>

      <motion.div
        whileHover={{ scale: 1.02 }}
        style={{
          padding: "2rem",
          borderRadius: "24px",
          background: "#0f172a",
          border: "1px solid rgba(34,197,94,0.2)",
          fontFamily: "monospace",
          maxWidth: "850px",
          margin: "0 auto",
          boxShadow: "0 0 40px rgba(34,197,94,.15)",
        }}
      >
        <p style={{ color: "#22c55e" }}>
          $ envforge diagnose
        </p>

        <p>✓ Python 3.11 Detected</p>
        <p>✓ CUDA Toolkit Available</p>
        <p>✓ NVIDIA GPU Compatible</p>
        <p>✓ Dependency Check Passed</p>

        <br />

        <p style={{ color: "#06b6d4" }}>
          ⚡ Generating Optimized Environment...
        </p>

        <p style={{ color: "#94a3b8" }}>
          Profile: PyTorch CUDA
        </p>

        <p style={{ color: "#22c55e" }}>
          Status: Ready To Deploy ✓
        </p>
      </motion.div>
    </div>
  </div>
</section>
<div
  style={{
    textAlign: "center",
    marginBottom: "4rem",
  }}
>
  <h2>Ready to Forge Your Environment?</h2>

  <p
    style={{
      color: "var(--text-secondary)",
      marginTop: "1rem",
    }}
  >
    Start building optimized AI environments in minutes.
  </p>
</div>
{/* Footer */}
<footer
  style={{
    marginTop: "4rem",
    padding: "5rem 0 2rem",
    borderTop: "1px solid rgba(255,255,255,0.08)",
    background:
      "linear-gradient(to bottom, rgba(255,255,255,0.02), rgba(255,255,255,0.01))",
  }}
>
  <div
    className="container"
    style={{
      display: "grid",
      gridTemplateColumns: "2fr 1fr 1fr 1fr",
      gap: "3rem",
    }}
  >
    {/* Brand */}
    <div>
      <h2
        style={{
          fontSize: "1.8rem",
          marginBottom: "1rem",
          background:
            "linear-gradient(to right,#22c55e,#06b6d4,#3b82f6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        EnvForge ⚡
      </h2>

      <p
        style={{
          color: "var(--text-secondary)",
          lineHeight: "1.8",
          maxWidth: "350px",
        }}
      >
        Build, diagnose and optimize AI/ML environments with confidence.
        Designed for developers who want faster setup, fewer errors and
        smarter workflows.
      </p>

      <div
        style={{
          marginTop: "1rem",
          display: "flex",
          gap: "0.8rem",
        }}
      >
        <span
          style={{
            padding: "6px 12px",
            borderRadius: "999px",
            background: "rgba(34,197,94,0.15)",
            border: "1px solid rgba(34,197,94,0.25)",
            fontSize: "0.85rem",
          }}
        >
          Open Source
        </span>

        <span
          style={{
            padding: "6px 12px",
            borderRadius: "999px",
            background: "rgba(59,130,246,0.15)",
            border: "1px solid rgba(59,130,246,0.25)",
            fontSize: "0.85rem",
          }}
        >
          AI Powered
        </span>
      </div>
    </div>

    {/* Product */}
    <div>
      <h4 style={{ marginBottom: "1rem" }}>
        Product
      </h4>

      <p>Profiles</p>
      <p>Diagnose</p>
      <p>Troubleshoot</p>
      <p>Script Generator</p>
    </div>

    {/* Resources */}
    <div>
      <h4 style={{ marginBottom: "1rem" }}>
        Resources
      </h4>

      <p>Documentation</p>
      <p>Guides</p>
      <p>API Reference</p>
      <p>FAQ</p>
    </div>

    {/* Community */}
    <div>
      <h4 style={{ marginBottom: "1rem" }}>
        Community
      </h4>

      <p>Contribute</p>
      <p>GitHub</p>
      <p>Report Issues</p>
      <p>Discussions</p>
    </div>
  </div>

  {/* Bottom Bar */}
  <div
    style={{
      marginTop: "4rem",
      paddingTop: "1.5rem",
      borderTop: "1px solid rgba(255,255,255,0.06)",
      textAlign: "center",
      color: "var(--text-secondary)",
    }}
  >
    <p>
      Built for Developers ❤️ • Powered by AI ⚡ • Open Source 🚀
    </p>
  </div>
</footer>
    </div>
  );
}
