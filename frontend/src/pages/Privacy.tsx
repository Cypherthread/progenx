import { Helmet } from 'react-helmet-async'

export default function Privacy() {
  return (
    <>
      <Helmet>
        <title>Privacy Policy | Progenx</title>
      </Helmet>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        <h1 className="text-3xl font-bold text-white mb-2">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: March 18, 2026</p>

        <div className="prose prose-invert prose-sm max-w-none space-y-6 text-gray-400">
          <p>Progenx ("we," "us," "our") respects your privacy. This Privacy Policy explains how we collect, use, disclose, and protect your information when you use the Progenx Platform.</p>

          <h2 className="text-lg font-semibold text-white mt-8">1. Information We Collect</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-800 rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-gray-800/50">
                  <th className="text-left p-3 text-gray-300 font-medium">Category</th>
                  <th className="text-left p-3 text-gray-300 font-medium">Examples</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                <tr><td className="p-3">Account Data</td><td className="p-3 text-gray-500">Email, name, hashed password</td></tr>
                <tr><td className="p-3">Design Prompts & Outputs</td><td className="p-3 text-gray-500">Plain-English descriptions, generated circuits, sequences</td></tr>
                <tr><td className="p-3">Chat & Refinement History</td><td className="p-3 text-gray-500">Iterative design conversations</td></tr>
                <tr><td className="p-3">Audit Logs & Safety Scores</td><td className="p-3 text-gray-500">User ID, actions, safety flags</td></tr>
                <tr><td className="p-3">Usage Metadata</td><td className="p-3 text-gray-500">Design count, rate-limit status</td></tr>
              </tbody>
            </table>
          </div>

          <h2 className="text-lg font-semibold text-white mt-8">2. How We Use Your Information</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Provide and improve the design pipeline</li>
            <li>Enforce rate limits and safety screening</li>
            <li>Generate safety scores and disclaimers</li>
            <li>Legal compliance (including biosecurity reporting if required)</li>
          </ul>
          <p className="text-xs text-gray-600">Legal basis: contract performance (GDPR Art. 6(1)(b)) and legitimate interest</p>

          <h2 className="text-lg font-semibold text-white mt-8">3. Third-Party Processors</h2>
          <ul className="list-disc list-inside space-y-2">
            <li><strong className="text-white">Anthropic Claude API</strong> (Pro tier): Your prompt is sent to Claude for circuit design. Anthropic does not use commercial/API data for model training and deletes logs after 7 days.</li>
            <li><strong className="text-white">Groq</strong> (Free tier): Your prompt is sent to Groq's hosted Llama model. Groq does not use API data for training.</li>
            <li><strong className="text-white">NCBI Entrez</strong> (all tiers): Public gene-sequence queries only. No personal data is sent.</li>
            <li><strong className="text-white">Stripe</strong> (Pro tier): Payment processing only.</li>
          </ul>

          <h2 className="text-lg font-semibold text-white mt-8">4. Data Retention</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Account data: until you delete your account</li>
            <li>Designs & history: up to 5 years or until deletion</li>
            <li>Audit logs & safety scores: 2 years</li>
            <li>We honor GDPR deletion requests within 30 days</li>
          </ul>

          <h2 className="text-lg font-semibold text-white mt-8">5. International Data Transfers</h2>
          <p>Data is processed in the United States. For EU/UK users, we rely on Standard Contractual Clauses (SCCs) with our processors.</p>

          <h2 className="text-lg font-semibold text-white mt-8">6. Your Rights (GDPR & CCPA)</h2>
          <p>You have the right to access, rectify, delete, port, or object to processing of your data. Contact <a href="mailto:legal@progenx.ai" className="text-cyan-400 hover:text-cyan-300">legal@progenx.ai</a> to exercise these rights. California residents: we do not sell your data.</p>

          <h2 className="text-lg font-semibold text-white mt-8">7. Cookies & Tracking</h2>
          <p>We use only essential JWT-based authentication. No persistent tracking cookies or third-party analytics at launch.</p>

          <h2 className="text-lg font-semibold text-white mt-8">8. Children's Privacy</h2>
          <p>The Platform is not directed to children under 18.</p>

          <h2 className="text-lg font-semibold text-white mt-8">9. EU AI Act & Biosecurity Compliance</h2>
          <p>We classify this as a general-purpose AI tool with built-in safeguards. All designs undergo mandatory safety scoring and dual-use screening. We comply with applicable provisions of the EU AI Act and IGSC gene-synthesis screening guidelines.</p>

          <h2 className="text-lg font-semibold text-white mt-8">10. Contact & Complaints</h2>
          <p>Privacy Officer: <a href="mailto:legal@progenx.ai" className="text-cyan-400 hover:text-cyan-300">legal@progenx.ai</a></p>
          <p>You may lodge a complaint with your local supervisory authority.</p>

          <p className="text-xs text-gray-600 mt-8">Material updates will be posted here with a new "Last Updated" date.</p>
        </div>
      </div>
    </>
  )
}
