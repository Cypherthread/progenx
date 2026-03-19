import { Helmet } from 'react-helmet-async'

export default function Terms() {
  return (
    <>
      <Helmet>
        <title>Terms of Service | Progenx</title>
      </Helmet>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        <h1 className="text-3xl font-bold text-white mb-2">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: March 18, 2026</p>

        <div className="prose prose-invert prose-sm max-w-none space-y-6 text-gray-400">
          <p>Welcome to Progenx (the "Platform"), operated by Progenx ("we," "us," or "our"), located in Hidden Hills, California 91302, United States. By accessing or using the Platform, you agree to these Terms of Service ("Terms"). If you do not agree, do not use the Platform.</p>

          <h2 className="text-lg font-semibold text-white mt-8">1. Description of Service</h2>
          <p>Progenx is an <strong className="text-white">educational and experimental</strong> AI-powered bioengineering design platform. It generates computational gene circuits, DNA sequences, plasmid maps, flux-balance-analysis (FBA) predictions, assembly plans, and safety scores based on your plain-English prompts.</p>
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 text-amber-300 text-sm font-medium">
            ALL OUTPUT IS FOR EDUCATIONAL AND EXPERIMENTAL PURPOSES ONLY. It is NOT LAB-READY and has NOT been validated in any wet lab.
          </div>

          <h2 className="text-lg font-semibold text-white mt-8">2. User Accounts & Eligibility</h2>
          <p>You must be at least 18 years old. You are responsible for maintaining the confidentiality of your account credentials. Free tier limited to 5 designs/month; Pro tier subject to Stripe billing.</p>

          <h2 className="text-lg font-semibold text-white mt-8">3. Prohibited Conduct (Biosecurity & Safety)</h2>
          <p>You agree <strong className="text-red-400">NOT</strong> to use the Platform to:</p>
          <ul className="list-disc list-inside space-y-1 text-gray-400">
            <li>Design, plan, or attempt to construct biological agents, pathogens, toxins, or any item on the US Select Agents list, Australia Group list, or any dual-use research of concern.</li>
            <li>Bypass or attempt to circumvent our mandatory safety scoring, screening, or pathogen/dual-use flagging.</li>
            <li>Generate designs intended for weaponization, bioweapons research, or any activity prohibited by IGSC gene-synthesis screening guidelines or applicable law.</li>
            <li>Upload prompts that request removal of safety features (kill switches, resistance markers, etc.).</li>
          </ul>
          <p>Violation may result in immediate account termination, reporting to authorities, and cooperation with law enforcement.</p>

          <h2 className="text-lg font-semibold text-white mt-8">4. User Content & Intellectual Property</h2>
          <p>You retain ownership of your input prompts and any designs you generate. You grant us a worldwide, royalty-free license to use, store, analyze, and improve our models with anonymized designs (never shared publicly without your explicit consent). We own the Platform, algorithms, and all underlying code.</p>

          <h2 className="text-lg font-semibold text-white mt-8">5. Disclaimers & No Warranty</h2>
          <p className="font-semibold text-white">THE SERVICE AND ALL OUTPUTS ARE PROVIDED "AS IS" AND "AS AVAILABLE." WE MAKE NO REPRESENTATIONS OR WARRANTIES of any kind, express or implied, including:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>That any generated sequence, FBA prediction, or assembly plan will function in vivo.</li>
            <li>That designs are free of errors, safe, or suitable for laboratory use.</li>
            <li>Any warranty of merchantability, fitness for a particular purpose, or non-infringement.</li>
          </ul>

          <h2 className="text-lg font-semibold text-white mt-8">6. Limitation of Liability</h2>
          <p>To the maximum extent permitted by law, Progenx's total liability shall not exceed the amount you paid us in the 12 months preceding the claim (or $100 if you used only the free tier). We are NOT liable for any biological, financial, or other damages arising from use of generated designs.</p>

          <h2 className="text-lg font-semibold text-white mt-8">7. Indemnification</h2>
          <p>You agree to indemnify and hold us harmless from any claims, damages, or liabilities arising from (a) your use of any design in a laboratory or real-world setting, (b) violation of these Terms, or (c) any biosecurity-related regulatory action.</p>

          <h2 className="text-lg font-semibold text-white mt-8">8. Payments & Subscriptions</h2>
          <p>Pro tier billed monthly via Stripe at $29. You may cancel anytime. No refunds for partial months.</p>

          <h2 className="text-lg font-semibold text-white mt-8">9. Termination</h2>
          <p>We may terminate or suspend your account for violation of these Terms, including any biosecurity flag.</p>

          <h2 className="text-lg font-semibold text-white mt-8">10. Governing Law</h2>
          <p>These Terms are governed by the laws of the State of California, without regard to conflict-of-laws principles. Venue: Los Angeles County courts.</p>

          <h2 className="text-lg font-semibold text-white mt-8">11. Changes to Terms</h2>
          <p>We will notify material changes via email or in-app banner. Continued use constitutes acceptance.</p>

          <p className="mt-8 text-gray-500">Contact: <a href="mailto:legal@progenx.ai" className="text-cyan-400 hover:text-cyan-300">legal@progenx.ai</a></p>
        </div>
      </div>
    </>
  )
}
