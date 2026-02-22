const ContactSection = () => {
    return (
        <section id="contact" className="py-24 bg-white">
            <div className="max-w-3xl mx-auto px-6 text-center">
                <h2 className="text-3xl font-semibold tracking-tight text-slate-900 mb-4">
                    Ready to streamline your deal flow?
                </h2>
                <p className="text-slate-500 mb-10">
                    Join the waiting list or get in touch to schedule a
                    personalized walkthrough of the Aviato platform
                </p>

                <form className="max-w-md mx-auto space-y-4 text-left">
                    <div>
                        <label className="block text-xs font-medium text-slate-700 mb-1.5">
                            Work Email
                        </label>
                        <input
                            type="email"
                            placeholder="investor@fund.vc"
                            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-slate-700 mb-1.5">
                            Message (Optional)
                        </label>
                        <textarea
                            rows={3}
                            placeholder="Tell us about your fund size and focus..."
                            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm resize-none"
                        ></textarea>
                    </div>
                    <button
                        type="button"
                        className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        Request Access
                    </button>
                </form>

                <p className="text-xs text-slate-400 mt-6">
                    Or email us directly at{" "}
                    <a
                        href="mailto:hello@aviato.vc"
                        className="text-blue-600 hover:underline"
                    >
                        hello@aviato.vc
                    </a>
                </p>
            </div>
        </section>
    );
};

export default ContactSection;
