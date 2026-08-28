import { useEffect, useState } from "react";
import { CircleAlert, X } from "lucide-react";

import "./ErrorToast.css";

type ErrorToastProps = {
    message: string;
    onClose: () => void;
    duration?: number;
};

export function ErrorToast({
    message,
    onClose,
    duration = 4000,
}: ErrorToastProps) {
    const [closing, setClosing] = useState(false);

    useEffect(() => {
        if (!message) return;

        setClosing(false);

        const timer = setTimeout(() => {
            setClosing(true);
        }, duration);

        return () => clearTimeout(timer);
    }, [message, duration]);

    if (!message) return null;

    function handleClose() {
        setClosing(true);
    }

    return (
        <div className="error-toast-container">
            <div
                className={`error-toast ${closing ? "closing" : ""}`}
                role="alert"
                aria-live="assertive"
                onAnimationEnd={() => {
                    if (closing) {
                        onClose();
                    }
                }}
            >
                <CircleAlert size={20} />

                <span>{message}</span>

                <button type="button" onClick={handleClose}>
                    <X size={18} />
                </button>
            </div>
        </div>
    );
}
