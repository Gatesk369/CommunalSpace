import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "motion/react";
import AuthBackground from "../components/AuthBackground";
import { requestPasswordReset } from "../api/auth";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthBackground>
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 2, ease: [1, 0, 0, 1] }}
        className="relative z-10 drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] bg-white rounded-[50%] w-[700px] h-[700px] flex flex-col items-center justify-center p-10 text-center"
      >
        {sent ? (
          <>
            <h1 className="text-cs-red text-[56px] font-semibold mb-6">
              Check your inbox
            </h1>
            <p className="text-lg mb-6">
              If an account exists for <strong>{email}</strong>, a reset link is
              on its way.
            </p>
            <Link to="/login" className="font-bold underline text-lg">
              Back to login
            </Link>
          </>
        ) : (
          <>
            <h1 className="text-cs-red text-[56px] font-semibold mb-6">
              Reset Password
            </h1>
            <form
              onSubmit={handleSubmit}
              className="w-[70%] flex flex-col gap-3"
            >
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
              />
              {error && (
                <p className="text-cs-red text-lg text-center">{error}</p>
              )}
              <motion.button
                whileTap={{ scale: 0.96 }}
                type="submit"
                className="bg-cs-orange text-white text-xl font-bold rounded-full py-3.5 mt-2"
              >
                Send Reset Link
              </motion.button>
            </form>
            <p className="text-lg mt-6">
              <Link to="/login" className="font-bold underline">
                Back to login
              </Link>
            </p>
          </>
        )}
      </motion.div>
    </AuthBackground>
  );
}
