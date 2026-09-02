import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "motion/react";
import AuthBackground from "../components/AuthBackground";
import { apiRequest } from "../api/client";

export default function VerifyEmailPage() {
  const { token } = useParams();
  const [status, setStatus] = useState("verifying");
  const [message, setMessage] = useState("");
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    apiRequest(`/accounts/verify-email/${token}/`)
      .then((data) => {
        setStatus("success");
        setMessage(data.detail);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.message);
      });
  }, [token]);

  // ...rest of the file is unchanged
  return (
    <AuthBackground>
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 2, ease: [1, 0, 0, 1] }}
        className="relative z-10 drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] bg-white rounded-[50%] w-[700px] h-[700px] flex flex-col items-center justify-center p-10 text-center"
      >
        {status === "verifying" && (
          <p className="text-xl">Verifying your account…</p>
        )}

        {status === "success" && (
          <>
            <h1 className="text-cs-red text-[56px] font-semibold mb-6">
              Verified!
            </h1>
            <p className="text-lg mb-6">{message}</p>
            <Link to="/login" className="font-bold underline text-lg">
              Go to login
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <h1 className="text-cs-red text-[56px] font-semibold mb-6">Oops</h1>
            <p className="text-lg mb-6">{message}</p>
            <Link to="/login" className="font-bold underline text-lg">
              Back to login
            </Link>
          </>
        )}
      </motion.div>
    </AuthBackground>
  );
}
