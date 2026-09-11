import type { InputHTMLAttributes } from "react";
import "./FormField.css";

type FormFieldProps = InputHTMLAttributes<HTMLInputElement> & {
    label: string;
};

export function FormField({ label, id, name, ...inputProps }: FormFieldProps) {
    const inputId = id ?? name;

    return (
        <div className="form-field">
            <label htmlFor={inputId}>{label}</label>

            <input
                id={inputId}
                name={name}
                className="form-field__input"
                {...inputProps}
            />
        </div>
    );
}
