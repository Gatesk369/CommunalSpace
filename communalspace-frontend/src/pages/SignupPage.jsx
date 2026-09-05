import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "motion/react";
import AuthBackground from "../components/AuthBackground";
import { signupRequest } from "../api/auth";
import LoadingButton from "../components/LoadingButton";

export default function SignupPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    const nameParts = fullName.trim().split(/\s+/);
    if (nameParts.length < 2) {
      setError("Please enter your first and last name.");
      setIsLoading(false);
      return;
    }
    if (!email) {
      setError("Please enter your email.");
      setIsLoading(false);
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      setIsLoading(false);
      return;
    }
    if (!confirmPassword) {
      setError("Confirm password cannot be empty.");
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      setIsLoading(false);
      return;
    }

    const [firstName, ...rest] = nameParts;
    const lastName = rest.join(" ");

    try {
      await signupRequest({ firstName, lastName, email, password });
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AuthBackground>
      <motion.div
        initial={{ scale: 0, opacity: 0, rotate: 0 }}
        animate={{ scale: 1, opacity: 1, rotate: [0, 20] }}
        transition={{
          scale: { duration: 2, delay: 0.6, ease: [1, 0, 0, 1] },
          opacity: { duration: 2, delay: 0.6, ease: [1, 0, 0, 1] },
          rotate: {
            duration: 11,
            repeat: Infinity,
            repeatType: "reverse",
            ease: [0.65, 0, 0.35, 1],
          },
        }}
        className="relative z-10 drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] bg-white rounded-[50%] w-[700px] h-[860px] flex flex-col items-center justify-center p-10"
      >
        <motion.div
          initial={{ opacity: 0, rotate: 0 }}
          animate={{ opacity: 1, rotate: [0, -20] }}
          transition={{
            opacity: { delay: 2.6, duration: 0.6, ease: "easeOut" },
            rotate: {
              duration: 11,
              repeat: Infinity,
              repeatType: "reverse",
              ease: [0.65, 0, 0.35, 1],
            },
          }}
          className="w-[600px] flex flex-col items-center justify-center p-10"
        >
          {success ? (
            <>
              <h1 className="text-cs-red text-[56px] font-semibold mb-6 text-center">
                Almost there!
              </h1>
              <p className="text-lg text-center mb-6">
                We&apos;ve sent a verification link to <strong>{email}</strong>.
                Confirm it to activate your account.
              </p>
              <Link to="/login" className="font-bold underline text-lg">
                Back to login
              </Link>
            </>
          ) : (
            <>
              <h1 className="text-cs-red text-[64px] font-semibold mb-6">
                New Here?
              </h1>

              <form
                onSubmit={handleSubmit}
                className="drop-shadow-md w-[70%] flex flex-col gap-3"
              >
                <input
                  type="text"
                  placeholder="Full Name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
                />
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
                />

                {error && (
                  <p className="text-cs-red text-lg text-center">{error}</p>
                )}

                <div className="w-full flex items-center justify-center">
                  <LoadingButton
                    type="submit"
                    isLoading={isLoading}
                    loadingText="Signing up..."
                  >
                    Sign Up
                  </LoadingButton>
                </div>
              </form>

              <p className="text-lg mt-6">
                Already have an account?{" "}
                <Link to="/login" className="font-bold underline">
                  Log in
                </Link>
              </p>
            </>
          )}
        </motion.div>
      </motion.div>
    </AuthBackground>
  );
}
