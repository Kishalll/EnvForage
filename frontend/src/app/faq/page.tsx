export default function FAQPage() {
  const faqs = [
    {
      question: "What is EnvForage?",
      answer: "EnvForage generates deterministic, hardware-aware setup scripts for PyTorch, CUDA, and GPU drivers so your ML environment works on the first try."
    },
    {
      question: "How do I install the CLI agent?",
      answer: "Run: pip install envforge-agent, then use envforge diagnose to scan your hardware."
    },
    {
      question: "Which GPUs are supported?",
      answer: "EnvForage supports NVIDIA GPUs with CUDA. AMD ROCm support is currently in development."
    },
    {
      question: "Is EnvForage free to use?",
      answer: "Yes, EnvForage is fully open-source under the MIT license."
    },
    {
      question: "Which ML frameworks does EnvForage support?",
      answer: "Currently PyTorch, TensorFlow, JAX, and YOLOv8 profiles are supported out of the box."
    }
  ];

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-4xl font-bold mb-4">Frequently Asked Questions</h1>
      <p className="text-gray-400 mb-10">
        Everything you need to know about EnvForage.
      </p>
      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <details key={index} className="border border-gray-700 rounded-lg p-4">
            <summary className="cursor-pointer font-semibold text-lg">
              {faq.question}
            </summary>
            <p className="mt-3 text-gray-400">{faq.answer}</p>
          </details>
        ))}
      </div>
    </main>
  );
}